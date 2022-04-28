# General SDK tests:
import time
import json
import struct
import unittest
import websocket
from unittest.mock import MagicMock, patch

from tenacity import RetryError

import verbit.streaming_client
from verbit.streaming_client import WebsocketStreamingClientSingleConnection, WebSocketStreamingClient

from tests.common import RESPONSES


class TestClientSDK(unittest.TestCase):

    # Close response data:
    # Implementing WebSocket 'OPCODE_CLOSE'
    # Receiving Connection Close Status Codes: Following RFC6455
    # See: https://websocket-client.readthedocs.io/en/latest/examples.html#receiving-connection-close-status-codes
    HAPPY_CLOSE_MSG = struct.pack("!H", websocket.STATUS_GOING_AWAY) + b"Test generator ended is the reason."
    UNEXPECTED_CLOSE_MSG = struct.pack("!H", websocket.STATUS_UNEXPECTED_CONDITION) + b"Test generator error testing."
    INVALID_UTF8_CLOSE_MSG = struct.pack("!H", 808) + b"\xc3\x28"

    def setUp(self):

        # fake
        self.access_token = "ABCD"

        self.client = WebSocketStreamingClient(access_token=self.access_token)

        self._media_status = {'started': False, 'finished': False}

        # init media generator
        self.valid_media_generator = self._fake_media_generator(num_samples=1600, num_chunks=500, media_status=self._media_status, delay_sec=0.0)
        self.infinite_valid_media_generator = self._fake_media_generator(num_samples=1600, num_chunks=500000000, media_status=self._media_status, delay_sec=0.1)

    def test_happy_flow(self):
        """
        Happy flow:
            1. responses arrive
            2. until there's a response with EOS
            3. client has called 'close()' after EOS
        """

        # mock websocket receive data func
        side_effects = [(websocket.ABNF.OPCODE_TEXT, RESPONSES['happy_json_resp0']),
                        (websocket.ABNF.OPCODE_TEXT, RESPONSES['happy_json_resp1']),
                        (websocket.ABNF.OPCODE_TEXT, RESPONSES['happy_json_resp_EOS'])]

        self._patch_ws_class(responses_mock=MagicMock(side_effect=side_effects))

        # start streaming mocked media (and mock connection)
        response_generator = self.client.start_with_media(media_generator=self.valid_media_generator)
        self.client._ws_client.connect.assert_called_once()
        self.assertTrue(self.client._ws_client.connected)

        # final response should only arrive after the whole media is streamed:
        # so we can just wait for media to end initially:
        self._wait_for_media_key(self._media_status, key='finished')

        # assert expected responses
        i = 0
        for i, response in enumerate(response_generator):
            self.assertEqual(response, self._json_to_dict(side_effects[i][1]))

        # assert that the right number of responses where indeed all consumed and checked above
        self.assertEqual(i, len(side_effects) - 1)

        # client close triggers sending an EOS message:
        self.client._ws_client.send.assert_called()
        arg0_client_eos_send = self.client._ws_client.send.call_args_list[0][0][0]
        self.assertIsInstance(arg0_client_eos_send, str, f'Given type: {type(arg0_client_eos_send).__name__}')
        self.assertIn('EOS', arg0_client_eos_send)

        # assert client closed after EOS response
        self.client._ws_client.close.assert_called_once()

        # check that ws is no longer connected
        self.assertFalse(self.client._ws_client.connected)

    def test_ws_connect_refuses_does_retry(self):
        """Client should raise an exception after re-tries timeout."""
        client = WebSocketStreamingClient(access_token=self.access_token)

        short_timeout_for_testing = 0.01
        client.max_connection_retry_seconds = short_timeout_for_testing

        def mock_connect_fail(_self, *_args, **_kwargs):
            raise websocket.WebSocketException("Connection rejected by mocking")

        # raises 'RetryError'
        with patch('verbit.streaming_client.WebSocket.connect', mock_connect_fail):
            with self.assertRaises(RetryError) as cm_raises:
                _ = client.start_with_media(media_generator=self.valid_media_generator)

        retry_err = cm_raises.exception
        last_exception = retry_err.last_attempt.exception()

        # where the retried exception was raised the 502 error above
        self.assertIsInstance(last_exception, websocket.WebSocketException)
        self.assertTrue(retry_err.last_attempt.failed)

        # at least one retry has been attempted
        self.assertGreater(retry_err.last_attempt.attempt_number, 1)

    def test_ws_connect_client_error_does_not_retry_401(self):
        client = WebSocketStreamingClient(access_token=self.access_token)

        short_timeout_for_testing = 0.01
        client.max_connection_retry_seconds = short_timeout_for_testing

        def mock_connect_fail_auth_401(_self, *_args, **_kwargs):
            raise websocket.WebSocketBadStatusException(message="Mocked Handshake status %d %s", status_code=401, status_message="Mocked Authentication rejected")

        # does not raise 'RetryError', but directly the raised error
        with patch('verbit.streaming_client.WebSocket.connect', mock_connect_fail_auth_401):
            with self.assertRaises(websocket.WebSocketBadStatusException):
                _ = client.start_with_media(media_generator=self.valid_media_generator)

    def test_ws_connect_client_server_busy_error_does_retry_502(self):
        client = WebSocketStreamingClient(access_token=self.access_token)

        short_timeout_for_testing = 0.01
        client.max_connection_retry_seconds = short_timeout_for_testing

        def mock_connect_fail_bad_gateway_502(_self, *_args, **_kwargs):
            raise websocket.WebSocketBadStatusException(message="Mocked Handshake status %d %s", status_code=502, status_message="Mocked Bad Gateway")

        # does raise 'RetryError'
        with patch('websocket.WebSocket.connect', mock_connect_fail_bad_gateway_502):
            with self.assertRaises(RetryError) as cm_raises:
                _ = client.start_with_media(media_generator=self.valid_media_generator)

        retry_err = cm_raises.exception
        last_exception = retry_err.last_attempt.exception()

        # while inside the 'retry': the raised exception was the '502 error' above
        self.assertIsInstance(last_exception, websocket.WebSocketBadStatusException)
        self.assertTrue(retry_err.last_attempt.failed)

        # at least one retry has been attempted
        self.assertGreater(retry_err.last_attempt.attempt_number, 1)

    def test_missing_required_init_params(self):

        with self.assertRaises(ValueError):
            WebSocketStreamingClient(access_token=None)

    def test_media_thread_exceptions(self):
        """Example of testing media errors on the media thread."""

        # init client
        client = WebSocketStreamingClient(access_token=self.access_token, on_media_error=MagicMock())

        ex = RuntimeError('Testing error propagation')

        media_status = {'started': False}

        def evil_media_gen():
            media_status['started'] = True
            yield b'fake'
            raise ex

        # mock
        self._patch_ws_class()

        # start evil stream
        client.start_with_media(media_generator=evil_media_gen())

        # wait for media-thread to actually run
        self._wait_for_media_key(media_status=media_status, key='started')

        # assert we get the expected exception
        client._on_media_error.assert_called_with(ex)

    def test_bad_media_generator(self):
        """Example of testing media errors on the media thread: media generator will yield an 'int' instead of 'bytes'."""

        # init client
        client = WebSocketStreamingClient(access_token=self.access_token, on_media_error=MagicMock())
        self._patch_ws_class()

        media_status = {'started': False, 'finished': False}

        def bad_media_gen():
            media_status['started'] = True

            # yield a valid chunk
            yield b'3123123'

            # yield an invalid chunk
            yield 3

            # unreachable, client code will raise and not continue after an invalid chunk
            media_status['finished'] = True

        # start evil stream
        client.start_with_media(media_generator=bad_media_gen())

        # wait for media-thread to actually run
        self._wait_for_media_key(media_status=media_status, key='started')

        # assert we get the expected exception
        client._on_media_error.assert_called_once()
        first_call_arg = client._on_media_error.call_args[0][0]
        self.assertIsInstance(first_call_arg, TypeError, f'Given type: {type(first_call_arg).__name__}')

    # ========================================== #
    # Test difference early 'close()' scenarios: #
    # ========================================== #
    def test_close_response(self):
        """CLOSE OPCODE Arrived before a response with EOS, that is, stream stopped in the middle."""

        self._test_close_common(self.HAPPY_CLOSE_MSG)

        # assert client closed after server closed
        self.client._ws_client.close.assert_called_once()

        # 'send' is only used for EOS by media ending, not expected here since media should still be streaming
        self.client._ws_client.send.assert_not_called()

    def test_close_unexpected_code(self):  # _Sometimes_ fails! since - media thread fails first.
        """CLOSE OPCODE in middle, with unexpected code"""

        # mock client logger
        self.client._logger.warning = MagicMock()

        self._test_close_common(self.UNEXPECTED_CLOSE_MSG)

        # assert client warning on unexpected close code
        self.assertIn('Unexpected close code', self.client._logger.warning.call_args_list[0][0][0])

        # assert client closed after server closed
        self.client._ws_client.close.assert_called_once()

        # 'send' is only used for EOS by media ending, not expected here since media should still be streaming
        self.client._ws_client.send.assert_not_called()

    def test_close_invalid_utf8(self):
        """CLOSE OPCODE in middle with invalid utf8"""

        # mock client logger
        self.client._logger.error = MagicMock()

        self._test_close_common(self.INVALID_UTF8_CLOSE_MSG)

        # assert client warning on unexpected close code
        self.assertIn('WebSocket closed with invalid payload', self.client._logger.error.call_args_list[0][0][0])

        # assert client closed after server closed
        self.client._ws_client.close.assert_called_once()

        # 'send' is only used for EOS by media ending, not expected here since media should still be streaming
        self.client._ws_client.send.assert_not_called()

    def test_data_ended_without_EOS(self):

        # mock websocket receive data func
        side_effect = [(websocket.ABNF.OPCODE_TEXT, RESPONSES['happy_json_resp0']),
                       (websocket.ABNF.OPCODE_TEXT, RESPONSES['happy_json_resp1'])]

        self._patch_ws_class(responses_mock=MagicMock(side_effect=side_effect))
        # start stream and expect StopIteration on third `next` call on generator, when generator is finished.
        response_generator = self.client.start_with_media(media_generator=self.valid_media_generator)
        next(response_generator)
        next(response_generator)
        with self.assertRaises(Exception):
            next(response_generator)

        # assert client closed after server closed
        self.client._ws_client.close.assert_called_once()

    def test_disconnect_while_streaming(self):
        """Test expected behavior of server disconnection while streamming for different client classes."""

        # exported client reconnects
        self._run_mocked_disconnecting_server(WebSocketStreamingClient)

    def test_disconnect_while_streaming__single_connection(self):
        """single-connection-client, does not reconnect by itself"""

        with self.assertRaises(ConnectionError):
            self._run_mocked_disconnecting_server(WebsocketStreamingClientSingleConnection)

    # ======= #
    # Helpers #
    # ======= #
    def _test_close_common(self, close_msg):

        # mock websocket receive data func
        side_effects = [(websocket.ABNF.OPCODE_TEXT, RESPONSES['happy_json_resp0']),
                        (websocket.ABNF.OPCODE_TEXT, RESPONSES['happy_json_resp0']),
                        (websocket.ABNF.OPCODE_TEXT, RESPONSES['happy_json_resp0']),
                        (websocket.ABNF.OPCODE_CLOSE, close_msg)]

        self._patch_ws_class(responses_mock=MagicMock(side_effect=side_effects))

        # start streaming mocked media (and mock connection)
        response_generator = self.client.start_with_media(media_generator=self.infinite_valid_media_generator)

        i = None
        for i, response in enumerate(response_generator):
            self.assertEqual(response, self._json_to_dict(side_effects[i][1]))

        # check all expected responses were consumed: meaning all OPCODE_TEXT messages:
        self.assertEqual(i, len(side_effects) - 2)

    def _run_mocked_disconnecting_server(self, ws_client_cls):
        """Run a scenario, creating a client instance and letting connect to a mocked server which disconnects and possibly resumes several times."""

        # init client
        client = ws_client_cls(access_token=self.access_token)

        # MagicMock behavior with 'side_effect' parameter:
        # Given a list of side effects: MagicMock will iterate through them:
        # 1. Given a class derived from Exception: the instance will be RAISED
        # 2. Give any other class, the instance will be RETURNED
        side_effects = [(websocket.ABNF.OPCODE_TEXT, RESPONSES['happy_json_resp0']),
                        (websocket.ABNF.OPCODE_TEXT, RESPONSES['happy_json_resp0']),
                        ConnectionResetError('Test disconnection before reconnect 1'),
                        (websocket.ABNF.OPCODE_TEXT, RESPONSES['happy_json_resp0']),
                        (websocket.ABNF.OPCODE_TEXT, RESPONSES['happy_json_resp0']),
                        ConnectionResetError('Test disconnection before reconnect 2'),
                        (websocket.ABNF.OPCODE_TEXT, RESPONSES['happy_json_resp0']),
                        (websocket.ABNF.OPCODE_TEXT, RESPONSES['happy_json_resp0']),
                        ConnectionResetError('Test disconnection before reconnect 3'),
                        (websocket.ABNF.OPCODE_TEXT, RESPONSES['happy_json_resp0']),
                        (websocket.ABNF.OPCODE_TEXT, RESPONSES['happy_json_resp_EOS'])]

        exception_count = sum(1 for x in side_effects if isinstance(x, Exception))
        respense_count = len(side_effects) - exception_count

        self._patch_ws_class(responses_mock=MagicMock(side_effect=side_effects))
        response_generator = client.start_with_media(media_generator=self.infinite_valid_media_generator)

        # consume all results except for the EOS:
        for i in range(respense_count - 1):
            response = next(response_generator)
            self.assertFalse(response['response']['is_end_of_stream'], f'Response {i} is expected to be EOS=False')

        # and now the EOS:
        last_response = next(response_generator)
        self.assertTrue(last_response['response']['is_end_of_stream'], f'Last response is expected to be EOS=True')

    @staticmethod
    def _fake_media_generator(num_samples, num_chunks, media_status: dict, delay_sec=0.1):
        """Fake media, of 16 bits per sample binary data"""
        try:
            media_status['started'] = True
            for _ in range(num_chunks):
                yield b'\xff\xf8' * num_samples
                time.sleep(delay_sec)

        finally:
            media_status['finished'] = True

    @staticmethod
    def _wait_for_media_key(media_status: dict, key, wait_interval=0.001):
        # wait for a specific key to change int 'media_status'
        while not media_status[key]:
            time.sleep(wait_interval)

        # and for 'send()' to be done afterwards:
        time.sleep(wait_interval)

    def _patch_ws_class(self, responses_mock=MagicMock()):
        """Patches the WebSocket class to have mocked methods, with success side effects.

        Returns: unpatch() closure

        Uses 'patch.object()' for binding methods before instance creation, with access to 'self'
        see: https://docs.python.org/3/library/unittest.mock-examples.html#mocking-unbound-methods

        The mocked methods 'self' parameter will be called '_self'
        while 'self' is the 'unittest-class' self-parameter.

        Installs a patch removing callback on teardown time using '.addCleanup()' which is the recommended practice.
        """

        def mock_connect_ok(_self, *_args, **_kwargs):
            _self.connected = True
            return unittest.mock.DEFAULT

        def mock_send_binary(_self, chunk):
            if not _self.connected:
                raise ConnectionError('Mocked WS disconnected called send_binary().')

            # if chunk has no 'len' (means it's not bytes) -> will raise an exception
            len(chunk)

            # if we've reached here, return default Mock() behavior.
            return unittest.mock.DEFAULT

        def mock_recv_data(_self):
            if not _self.connected:
                raise ConnectionError('Mocked WS disconnected called recv_data().')

            return responses_mock()

        def mock_close(_self, *_args, **_kwargs):
            _self.connected = False
            return unittest.mock.DEFAULT

        # patch relevant methods
        patchers = (
            patch.object(verbit.streaming_client.WebSocket, 'connect', autospec=True, side_effect=mock_connect_ok),
            patch.object(verbit.streaming_client.WebSocket, 'send_binary', autospec=True, side_effect=mock_send_binary),
            patch.object(verbit.streaming_client.WebSocket, 'recv_data', autospec=True, side_effect=mock_recv_data),
            patch.object(verbit.streaming_client.WebSocket, 'send', autospec=False),
            patch.object(verbit.streaming_client.WebSocket, 'close', autospec=True, side_effect=mock_close),
        )

        # start all patchers
        for patcher in patchers:
            patcher.start()

        def unpatch():
            for p in patchers:
                p.stop()

        # stop these patchers at end of current test-case
        self.addCleanup(unpatch)

        return unpatch

    @staticmethod
    def _json_to_dict(j: bytes):
        return json.loads(j.decode('utf-8'))
