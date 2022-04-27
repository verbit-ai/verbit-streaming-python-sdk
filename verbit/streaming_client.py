#!/usr/bin/env python3

import json
import socket
import struct
import typing
import logging
from enum import IntFlag
from threading import Thread
from dataclasses import dataclass
from urllib.parse import urlencode

import tenacity
from tenacity import retry, wait_random_exponential, stop_after_delay
from websocket import WebSocket, WebSocketException, WebSocketBadStatusException, ABNF, STATUS_NORMAL, STATUS_GOING_AWAY


@dataclass
class MediaConfig:
    format: str = 'S16LE'       # signed 16-bit little-endian PCM
    sample_rate: int = 16000    # in Hz
    sample_width: int = 2       # in bytes
    num_channels: int = 1


class ResponseType(IntFlag):
    Transcript = 1
    Captions = 2

    @classmethod
    def from_name(cls, name: str):
        title = name.title()
        return cls.__members__.get(title)


class WebsocketStreamingClientSingleConnection:

    # constants
    DEFAULT_CONNECT_TIMEOUT_SECONDS = 120.0

    # events
    EVENT_EOS = 'EOS'

    # connection related exception classes:
    #  1. WebSocketException: Raised from remote WebSocket connection
    #  2. ConnectionError: Raised when WebSocket is on the same local machine
    #  3. TimeoutError: From OS-level, for example when physically disconnecting from a network results in a timeout
    #  4. socket.timeout/socket.gaierror: Are merged into '3' in python 3.10, but required in earlier python versions
    CONNECTION_EXCEPTION_CLASSES = (WebSocketException, ConnectionError, TimeoutError, socket.timeout, socket.gaierror)

    # retry related http status codes
    RETRY_HTTP_4XX_CODES = (429,)
    NO_RETRY_HTTP_5XX_CODES = (501, 505, 506, 507, 508, 510)

    def __init__(self, access_token, on_media_error: typing.Callable[[Exception], None] = None):

        # assert arguments
        if not access_token:
            raise ValueError("Parameter 'access_token' is required")

        # media config
        self._media_config = None

        self._max_connection_retry_seconds = self.DEFAULT_CONNECT_TIMEOUT_SECONDS

        # ASR config
        self._model_id = None
        self._language_code = None

        # server url
        self._schema = 'wss'
        self._base_url = "speech.verbit.co"
        self._server_path = '/ws'

        # WebSocket
        self._ws_client = None
        self._ws_access_token = access_token

        # logger
        self._logger = None
        self.set_logger()

        # internal
        self._media_sender_thread = None
        self._stop_media_thread = False
        self._response_types = 0
        self._eos_response_types = 0

        # error handling
        self._on_media_error = on_media_error or self._default_on_media_error

    # ========== #
    # Properties #
    # ========== #
    @property
    def ws_url(self) -> str:
        return f'{self._schema}://{self._base_url}{self._server_path}'

    @property
    def max_connection_retry_seconds(self) -> float:
        return self._max_connection_retry_seconds

    @max_connection_retry_seconds.setter
    def max_connection_retry_seconds(self, val: float):
        self._max_connection_retry_seconds = val

    # ========= #
    # Interface #
    # ========= #
    def start_stream(self,
                     media_generator,
                     media_config: MediaConfig = None,
                     response_types: ResponseType = ResponseType.Transcript) -> typing.Iterator[typing.Dict]:
        """
        Start streaming media and get back speech recognition responses from server.

        :param media_generator: a generator of media bytes chunks to stream over WebSocket for speech recognition
        :param media_config:     a MediaConfig dataclass which describes the media format sent by the client
        :param response_types:  a bitmask Flag denoting which response type(s) should be returned by the service

        :return: a generator which yields speech recognition responses (transcript, captions or both)
        """

        # use default media config if not provided
        media_config = media_config or MediaConfig()
        self._response_types = response_types

        # connect to WebSocket
        self._logger.info(f'Connecting to WebSocket at {self.ws_url}')
        self._connect_websocket(media_config=media_config, response_types=response_types)
        self._logger.info('WebSocket connected!')

        # start media sender thread
        self._media_sender_thread = Thread(
            target=self._media_sender_worker,
            args=(media_generator, ),
            name='ws_media_sender')
        self._stop_media_thread = False
        self._media_sender_thread.start()

        # return response generator
        return self._response_generator()

    def send_event(self, event: str, payload: dict = None):
        if self._ws_client is None or not self._ws_client.connected:
            raise RuntimeError('WebSocket client is disconnected!')
        self._send_event(event, payload)

    def send_eos_event(self):
        self._logger.debug(f'Sending EOS event')
        self.send_event(event=self.EVENT_EOS)

    def set_logger(self, logger: logging.Logger = None):
        """
        Set the streaming client logger object to an external logging.Logger

        :param logger: the external logger to use as the streaming client's logger
        :return:
        """

        # if logger object not provided
        if logger is None:

            # create logger
            logger = logging.getLogger(self.__class__.__name__)
            logger.setLevel(logging.DEBUG)

            # create console handler and set level to debug
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)

            # create formatter
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

            # add formatter to ch
            ch.setFormatter(formatter)

            # add ch to logger
            logging.basicConfig(handlers=[ch])

        self._logger = logger

    # ======== #
    # Internal #
    # ======== #
    def _connect_websocket(self, media_config: MediaConfig, response_types: ResponseType):
        """
        Connect to the URL returned by
            self.ws_url
        Retrying to connect up to
            self.max_connection_retry_seconds

        Retry policy:
        Connect to WebSocket service, using random-exponential-wait, explanation of why this is a good policy
        is explained in the AWS Architecture Blog
        Exponential Backoff And Jitter by Marc Brooker:
        https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/

        Which is linked and documented in tenacity:
        https://tenacity.readthedocs.io/en/latest/api.html#wait-functions

        :param media_config:    a MediaConfig dataclass which describes the media format sent by the client
        :param response_types: a bitmask Flag denoting which response type(s) should be returned by the server
        """

        # build WebSocket url
        ws_url = self.ws_url + self._get_ws_connect_query_string(media_config=media_config, response_types=response_types)

        # create WebSocket instance
        self._ws_client = WebSocket(enable_multithread=True)

        # set WebSocket client timeout
        self._ws_client.timeout = 20.0

        def _retry_http_error_predicate(retry_ex: WebSocketBadStatusException):

            # specific 4xx Client-Errors trigger retry
            if retry_ex.status_code in self.RETRY_HTTP_4XX_CODES:
                return True

            # don't retry all other 4xx client-errors
            if 400 <= retry_ex.status_code < 500:
                return False

            # specific 5xx Server-Errors not to retry:
            if retry_ex.status_code in self.NO_RETRY_HTTP_5XX_CODES:
                return False

            # retry all other 5xx server-errors:
            elif 500 <= retry_ex.status_code < 600:
                return True

            # don't retry all other errors codes
            return False

        def retry_predicate(retry_state: tenacity.RetryCallState):
            """Returning True - means retry, False - means do not."""

            outcome: tenacity.Future = retry_state.outcome
            if not outcome.failed:
                # Non-exception should not be retried
                return False

            # outcome was an exception
            outcome_ex: Exception = outcome.exception()

            # default is to not retry
            should_retry = False

            # http errors that may be retried
            if isinstance(outcome_ex, WebSocketBadStatusException):
                should_retry = _retry_http_error_predicate(outcome_ex)

            # exception types that should always be retried
            elif isinstance(outcome_ex, self.CONNECTION_EXCEPTION_CLASSES):
                should_retry = True

            self._logger.warning(f'Error while connecting WebSocket: {repr(outcome_ex)}, {should_retry=}')

            return should_retry

        @retry(wait=wait_random_exponential(multiplier=0.5),
               stop=stop_after_delay(self.max_connection_retry_seconds),
               retry=retry_predicate)
        def connect_and_retry():
            self._ws_client.connect(ws_url, header=self._get_ws_connect_headers())

        # try opening WebSocket connection
        try:
            connect_and_retry()

        # catch and log retry errors
        except tenacity.RetryError as retry_err:
            statistics = connect_and_retry.retry.statistics
            last_exception = retry_err.last_attempt.exception()
            self._logger.error(f'Error while connecting WebSocket! Exceeded maximum retries and giving up.\n'
                               f'Last attempt raised: {repr(last_exception)}\n'
                               f'Retry {statistics=}')

            # raise further so that exception can be handled
            raise

        # catch and log all other exceptions
        except Exception as ex:
            self._log_exception('Error while connecting WebSocket', ex)
            raise

    def _log_exception(self, msg: str, ex: Exception):
        self._logger.error(f'{msg}: {repr(ex)}')
        self._logger.debug(f'{msg}, stack trace:', exc_info=True)

    def _default_on_media_error(self, err: Exception):
        self._log_exception('Exception on media thread', err)

    def _send_event(self, event: str, payload: dict = None):

        # use default payload if not provided
        payload = payload or dict()

        # prepare message dict
        msg = dict(event=event, payload=payload)

        # serialize as json
        msg_json = json.dumps(msg)

        # send to server
        self._ws_client.send(msg_json)

    def _media_sender_worker(self, media_generator: typing.Iterator[bytes]):
        """Thread function for emitting media from a user-given generator."""

        try:

            # capture WebSocket, so that connect changes in other threads do not affect this loop
            ws_client = self._ws_client

            # iterate media generator
            for chunk in media_generator:

                # emit media chunk
                ws_client.send_binary(chunk)

                if self._stop_media_thread:
                    self._logger.debug(f'Stopping media thread')
                    return


            self._logger.debug(f'Finished sending media')

            # signal end of stream
            self.send_eos_event()

            self._logger.debug(f'Media sender finished')

        except Exception as err:
            self._on_media_error(err)

    def _response_generator(self) -> typing.Iterator[typing.Dict]:
        """
        Generator function for iterating responses.

        For available response structures, see: https://verbit.co/api_docs/index.html
        For a description of ABNF opcodes, see: https://datatracker.ietf.org/doc/html/rfc6455#section-5.2
        """

        # WebSocket should already be connected at this point, see: start_stream()
        if self._ws_client is None or not self._ws_client.connected:
            raise RuntimeError('WebSocket client is disconnected!')

        # init closing flag
        should_stop = False

        try:

            self._logger.debug('Waiting for responses ...')

            # as long as connection is open and receiving responses
            while not should_stop:

                # read data from WebSocket
                opcode, data = self._ws_client.recv_data()

                # message is text
                if opcode == ABNF.OPCODE_TEXT:

                    # parse from json
                    resp = json.loads(data.decode('utf-8'))

                    # update end-of-stream response types flag
                    received_eos_response = resp['response'].get('is_end_of_stream', False)
                    if received_eos_response:
                        response_type = ResponseType.from_name(resp['response']['type'])
                        if response_type is None:
                            self._logger.warning(f"Received reply with unknown 'type' field: {resp['response']['type']}.")
                        else:
                            self._eos_response_types |= response_type

                    # explicitly close on final response:
                    # since the 'finally' block will only run at GC time of the generator:
                    if self._eos_response_types == self._response_types:
                        self._close_ws()
                        should_stop = True

                    # response is ready
                    yield resp

                # message is close signal
                elif opcode == ABNF.OPCODE_CLOSE:

                    # handle close
                    self._handle_socket_close(data)

                    # update closing flag
                    should_stop = True

                else:

                    # future server versions might use more opcodes
                    self._logger.warning(f'Unexpected WebSocket response: OPCODE={opcode}')

        # catch connection errors (and don't try closing connection)
        except self.CONNECTION_EXCEPTION_CLASSES as connection_error:
            self._log_exception('Connection error while generating responses', connection_error)

            # raise further so that exception can be handled
            raise

        # catch all other exceptions
        except Exception as ex:
            self._log_exception('Error while generating responses', ex)

            # try to close WebSocket connection
            self._close_ws()

            # raise further so that exception can be handled
            raise

        # finished with no errors
        else:

            # try to close WebSocket connection
            self._close_ws()

    def _close_ws(self):
        """Close WebSocket if still connected."""
        # stop media thread
        self._stop_media_thread = True

        if self._ws_client.connected:
            self._logger.debug(f'Closing WebSocket')
            self._ws_client.close(STATUS_GOING_AWAY)


    def _handle_socket_close(self, data):
        """
        Implementing WebSocket 'OPCODE_CLOSE'
        Receiving Connection Close Status Codes: Following RFC6455
        https://websocket-client.readthedocs.io/en/latest/examples.html#receiving-connection-close-status-codes
        """

        try:

            # parse code and reason
            code = struct.unpack("!H", data[0:2])[0]
            reason = data[2:].decode('utf-8')

            # check if close code signals a problem
            msg = f'WebSocket closed. Code={code}, Reason={reason}'
            if code not in (STATUS_NORMAL, STATUS_GOING_AWAY):
                self._logger.warning('Unexpected close code: ' + msg)
            else:
                self._logger.debug(msg)

        except Exception as ex:
            self._log_exception(f'WebSocket closed with invalid payload. Data={data}', ex)

    def _get_ws_connect_headers(self) -> dict:
        return {**self._get_ws_auth_info()}

    @staticmethod
    def _get_ws_connect_query_string(media_config: MediaConfig, response_types: ResponseType) -> str:
        return '?' + urlencode({
            'format': media_config.format,
            'sample_rate': media_config.sample_rate,
            'sample_width': media_config.sample_width,
            'num_channels': media_config.num_channels,
            'get_transcript': bool(response_types & ResponseType.Transcript),
            'get_captions': bool(response_types & ResponseType.Captions),
        })

    def _get_ws_auth_info(self) -> dict:
        return {'Authorization': f'Bearer {self._ws_access_token}'}


class WebSocketStreamingClientReconnecting(WebsocketStreamingClientSingleConnection):
    """
    Extend the WebsocketStreamingClientSingleConnection class
    to reconnect to a server and continue after disconnection
    (for whatever reason).
    """

    def __init__(self, access_token, on_media_error: typing.Callable[[Exception], None] = None):

        # base class init logic
        super().__init__(access_token, on_media_error)

        # state for reconnection
        self._media_generator = None
        self._media_config = None
        self._response_types = None

    def start_stream(self,
                     media_generator,
                     media_config: MediaConfig = None,
                     response_types: ResponseType = ResponseType.Transcript) -> typing.Iterator[typing.Dict]:

        # store state for reconnection
        self._media_generator = media_generator
        self._media_config = media_config
        self._response_types = response_types

        # start stream now
        response_generator = super().start_stream(self._media_generator, self._media_config, self._response_types)

        return self._reconnect_generator(response_generator)

    def _reconnect_generator(self, response_generator) -> typing.Iterator[typing.Dict]:
        """
        Returns a generator wrapping `response_generator` which will attempt
        to reconnect in case of disconnection and keep on yielding results.
        """

        ended = False

        # continue until finished successfully
        while not ended:

            try:
                yield from response_generator

                # response_generator exhausted without any exceptions
                ended = True

            # catch connection errors and attempt reconnection
            except self.CONNECTION_EXCEPTION_CLASSES as connection_error:
                self._log_exception(f'Error while generating responses', connection_error)

                # wait for other threads, that still access the web-socket to fail and stop
                self._wait_for_thread(timeout_step=0.1, global_timeout=1.0)

                # try reconnecting and keep on yielding from the same generator
                self._logger.debug('Trying to reconnect')
                response_generator = super().start_stream(self._media_generator, self._media_config, self._response_types)

            # catch all other exceptions and stop the generator
            except Exception as ex:
                self._log_exception('Exception while reconnecting', ex)
                raise

    def _wait_for_thread(self, timeout_step: float, global_timeout: float):
        """Join thread, with logging on success status, and a timeout."""
        waiting_for = 0.0

        # request media thread to logically stop
        self._stop_media_thread = True

        while self._media_sender_thread.is_alive() and waiting_for < global_timeout:
            self._media_sender_thread.join(timeout=timeout_step)
            if self._media_sender_thread.is_alive():
                waiting_for += timeout_step
                self._logger.debug(f'{self._media_sender_thread.name} not closing, {waiting_for=} seconds...')
            else:
                self._logger.debug(f'{self._media_sender_thread.name} closed, {waiting_for=} seconds...')


# type alias for default exported Client class
WebSocketStreamingClient = WebSocketStreamingClientReconnecting
