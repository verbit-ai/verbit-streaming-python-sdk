#!/usr/bin/env python3

import json
import struct
import typing
import logging
from threading import Thread
from dataclasses import dataclass
from urllib.parse import urlencode

from tenacity import retry, wait_random_exponential, stop_after_delay
from websocket import WebSocket, ABNF, STATUS_NORMAL, STATUS_GOING_AWAY


@dataclass
class MediaConfig:
    format: str = 'S16LE'       # signed 16-bit little-endian PCM
    sample_rate: int = 16000    # in Hz
    sample_width: int = 2       # in bytes
    num_channels: int = 1


class SpeechStreamClient:

    # constants
    DEFAULT_CONNECT_TIMEOUT_SECONDS = 60.0

    # events
    EVENT_EOS = 'EOS'

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

        # web socket
        self._schema = 'wss'
        self._base_url = "speech.verbit.co"
        self._server_path = '/ws'
        self._ws_client = WebSocket(enable_multithread=True)
        self._ws_access_token = access_token

        # internal
        self._logger = logging.getLogger(self.__class__.__name__)
        self._media_sender_thread = None

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
    def start_stream(self, media_generator, media_config: MediaConfig = None) -> typing.Generator:
        """Start streaming media, returns a response generator."""

        # use default media config if not provided
        media_config = media_config or MediaConfig()

        # connect to websocket
        self._connect_websocket(media_config=media_config)

        # start media sender thread
        self._media_sender_thread = Thread(
            target=self._media_sender_worker,
            args=(media_generator, ),
            name='ws_media_sender')
        self._media_sender_thread.start()

        # return response generator
        return self._response_generator()

    def send_event(self, event: str, payload: dict = None):

        # use default payload if not provided
        payload = payload or dict()

        # prepare message dict
        msg = dict(event=event, payload=payload)

        # serialize as json
        msg_json = json.dumps(msg)

        # send to server
        self._ws_client.send(msg_json)

    # ======== #
    # Internal #
    # ======== #
    def _connect_websocket(self, media_config: MediaConfig):
        """
        Connect to the URL returned by
            self.ws_url
        Retrying to connect up to
            self.max_connection_retry_seconds

        Retry policy:
        Connect to websocket service, using random-exponential-wait, explanation of why this is a good policy
        is explained in the AWS Architecture Blog
        Exponential Backoff And Jitter by Marc Brooker:
        https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/

        Which is linked and documented in tenacity:
        https://tenacity.readthedocs.io/en/latest/api.html#wait-functions

        :param media_config: a MediaConfig dataclass which describes the media format sent by the client
        """

        # build websocket url
        ws_url = self.ws_url + self._get_ws_connect_query_string(media_config=media_config)

        try:

            @retry(wait=wait_random_exponential(multiplier=0.5,  max=60), stop=stop_after_delay(self.max_connection_retry_seconds))
            def connect_and_retry():

                # open websocket connection
                self._ws_client.connect(ws_url, header=self._get_ws_connect_headers())

            # connect
            connect_and_retry()

        except Exception:
            self._logger.exception(f'Error connecting WebSocket!')
            raise

    def _default_on_media_error(self, err: Exception):
        self._logger.exception(f'Exception on media thread!')

    def _media_sender_worker(self, media_generator):
        """Thread function for emitting media from a user-given generator."""

        try:

            # iterate media generator
            for chunk in media_generator:

                # emit media chunk
                self._ws_client.send_binary(chunk)

            # signal end of stream
            self.send_event(event=self.EVENT_EOS)
            self._logger.debug(f'Finished sending media')

        except Exception as err:
            self._on_media_error(err)

    def _response_generator(self):
        """Generator function for yielding responses."""

        # ws is already connected at this point, see: start_stream()
        if not self._ws_client.connected:
            raise RuntimeError('WebSocket client is disconnected!')

        # init final response flag
        received_final_response = False

        try:

            while not received_final_response:

                # read data from websocket
                opcode, data = self._ws_client.recv_data()

                # message is text
                if opcode == ABNF.OPCODE_TEXT:

                    # parse from json
                    resp = json.loads(data.decode('utf-8'))

                    # update final response flag
                    received_final_response = resp['response'].get('is_end_of_stream', False)

                    # explicitly close on final response:
                    # since the 'finally' block will only run at some system dependant cleanup time.
                    if received_final_response:
                        self._close_ws()
                    yield resp

                # message is close signal
                elif opcode == ABNF.OPCODE_CLOSE:

                    # handle close
                    self._handle_socket_close(data)
                    break

                else:

                    # Not an error, future server versions might use more opcodes.
                    self._logger.warning(f'Unexpected WebSocket response: OPCODE={opcode}')
        finally:
            self._close_ws()

    def _close_ws(self):
        """Close WebSocket if still connected."""
        if self._ws_client.connected:
            self._logger.debug(f'Closing WebSocket')
            self._ws_client.close(STATUS_GOING_AWAY)
        else:
            self._logger.debug(f'WebSocket already closed')

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

        except Exception:
            self._logger.exception(f'WebSocket closed with invalid payload. Data={data}')

    def _get_ws_connect_headers(self):
        return {**self._get_ws_auth_info()}

    @staticmethod
    def _get_ws_connect_query_string(media_config: MediaConfig) -> str:
        return '?' + urlencode({
            'format': media_config.format,
            'sample_rate': media_config.sample_rate,
            'sample_width': media_config.sample_width,
            'num_channels': media_config.num_channels
        })

    def _get_ws_auth_info(self):
        return {'Authorization': f'Bearer {self._ws_access_token}'}
