import time
import json
import struct
import unittest
import websocket
import pkg_resources
from os import path
from unittest.mock import MagicMock, patch
# from tenacity import RetryError

from verbit.streaming_client import SpeechStreamClient

from examples import example_client


# Load test resources:
def _load_json_resource(name):
    rel_path = pkg_resources.resource_filename(__name__, path.join('resources', name + '.json'))
    with open(rel_path, 'rb') as f:
        json_bytes = f.read()
    return json_bytes


RESOURCE_KEYS = ['happy_json_resp0', 'happy_json_resp1', 'happy_json_resp_EOS']
# init mock responses
RESPONSES = {k: _load_json_resource(k) for k in RESOURCE_KEYS}


# -----------
# General SDK tests:
class TestClientSDK(unittest.TestCase):

    # Close responses data:
    # Implementing WebSocket 'OPCODE_CLOSE'
    # Receiving Connection Close Status Codes: Following RFC6455
    # See: https://websocket-client.readthedocs.io/en/latest/examples.html#receiving-connection-close-status-codes
    HAPPY_CLOSE_MSG = struct.pack("!H", websocket.STATUS_GOING_AWAY) + b"Test generator ended is the reason."
    UNEXPECTED_CLOSE_MSG = struct.pack("!H", websocket.STATUS_UNEXPECTED_CONDITION) + b"Test generator error testing."
    INVALID_UTF8_CLOSE_MSG = struct.pack("!H", 808) + b"\xc3\x28"

    # Mock responses data:

    def setUp(self):

        # fake
        self.access_token = "ABCD"

        # init and patch client
        self.client = SpeechStreamClient(access_token=self.access_token)
        self._patch_client(self.client)

        # init media generator
        self.valid_media_generator = self._fake_media_generator(num_samples=1600, num_chunks=10, delay_sec=0.001)


    def test_happy_flow(self):
        """
        Happy flow:
            1. responses arrive
            2. until there's a response with EOS
            3. client has called 'close()' after EOS
        """

        # mock websocket receive data func
        side_effect = [(websocket.ABNF.OPCODE_TEXT, RESPONSES['happy_json_resp0']),
                       (websocket.ABNF.OPCODE_TEXT, RESPONSES['happy_json_resp1']),
                       (websocket.ABNF.OPCODE_TEXT, RESPONSES['happy_json_resp_EOS'])]
        self.client._ws_client.recv_data = MagicMock(side_effect=side_effect)

        # check that ws is not yet connected
        self.assertFalse(self.client._ws_client.connected)

        # start streaming mocked media (and mock connection)
        response_generator = self.client.start_stream(media_generator=self.valid_media_generator)
        self.client._ws_client.connect.assert_called_once()
        self.assertTrue(self.client._ws_client.connected)

        # assert expected responses
        for i, response in enumerate(response_generator):
            self.assertEqual(response, self._json_to_dict(side_effect[i][1]))
            time.sleep(0.01)

        # client close triggers sending an EOS message:
        arg0_client_eos_send = self.client._ws_client.send.call_args_list[0][0][0]
        self.assertIsInstance(arg0_client_eos_send, str, f'Given type: {type(arg0_client_eos_send)}')
        self.assertIn('EOS', arg0_client_eos_send)

        # assert client closed after EOS response
        self.client._ws_client.close.assert_called_once()

        # check that ws is no longer connected
        self.assertFalse(self.client._ws_client.connected)

    def test_close_response(self):
        """CLOSE OPCODE Arrived before a response with EOS, that is, stream stopped in the middle."""

        self._test_close_common(self.HAPPY_CLOSE_MSG)

        # assert client closed after server closed
        self.client._ws_client.close.assert_called_once()

        # 'send' is only used for EOS by media ending, not expected here since media should still be streaming
        self.client._ws_client.send.assert_not_called()

    # def test_ws_connect_refuses_raises(self):
    #     """When disabling ws_connect retries, client should fail raising an exception; without disabling it will simply take very long to test."""
    #     client = SpeechStreamClient(access_token=self.access_token,
    #                                 stream_id=self.stream_id)
    #     client.max_connection_retry_seconds=1

    #     def mock_connect_fail(self, *args, **kwargs):
    #         raise websocket.WebSocketException("Connection rejected by mocking")

    #     with patch('websocket.WebSocket.connect', mock_connect_fail):
    #         with self.assertRaises(RetryError):
    #             _ = client.start_stream(media_generator=self.valid_media_generator)

    # def test_close_unexpected_code(self):  # _Sometimes_ fails! since - media thread fails first.
    #     """CLOSE OPCODE in middle, with unexpected code"""

    #     # mock client logger
    #     self.client._logger.warning = MagicMock()

    #     self._test_close_common(self.UNEXPECTED_CLOSE_MSG)

    #     # assert client warning on unexpected close code
    #     self.assertTrue('Unexpected close code' in self.client._logger.warning.call_args_list[0][0][0])

    #     # assert client closed after server closed
    #     self.client._ws_client.close.assert_called_once()

    #     # 'send' is only used for EOS by media ending, not expected here since media should still be streaming
    #     self.client._ws_client.send.assert_not_called()

    # def test_close_invalid_utf8(self):
    #     """CLOSE OPCODE in middle with invalid utf8"""

    #     # mock client logger
    #     self.client._logger.exception = MagicMock()

    #     self._test_close_common(self.INVALID_UTF8_CLOSE_MSG)

    #     # assert client warning on unexpected close code
    #     self.assertTrue('WebSocket closed with invalid payload' in self.client._logger.exception.call_args_list[0][0][0])

    #     # assert client closed after server closed
    #     self.client._ws_client.close.assert_called_once()

    #     # 'send' is only used for EOS by media ending, not expected here since media should still be streaming
    #     self.client._ws_client.send.assert_not_called()

    # def test_data_ended_without_EOS(self):

    #     # mock websocket receive data func
    #     side_effect = [(websocket.ABNF.OPCODE_TEXT, RESPONSES['happy_json_resp0']),
    #                    (websocket.ABNF.OPCODE_TEXT, RESPONSES['happy_json_resp1'])]
    #     self.client._ws_client.recv_data = MagicMock(side_effect=side_effect)

    #     # start stream and expect StopIteration on third `next` call on generator
    #     response_generator = self.client.start_stream(media_generator=self.valid_media_generator)
    #     next(response_generator)
    #     next(response_generator)
    #     with self.assertRaises(Exception):
    #         next(response_generator)

    #     # assert client closed after server closed
    #     self.client._ws_client.close.assert_called_once()

    # def test_missing_required_init_params(self):

    #     with self.assertRaises(ValueError):
    #         SpeechStreamClient(stream_id=self.stream_id, access_token=None)
    #     with self.assertRaises(ValueError):
    #         SpeechStreamClient(stream_id=None, access_token=self.access_token)

    # def test_media_thread_exceptions(self):
    #     """Example of testing media errors on the media thread."""

    #     # init client
    #     client = SpeechStreamClient(access_token=self.access_token, stream_id=self.stream_id, on_media_error=MagicMock())

    #     ex = RuntimeError('Testing error propagation')

    #     def evil_media_gen():
    #         yield 'fake'
    #         raise ex

    #     # mock
    #     client._ws_client.connect = MagicMock()
    #     client._ws_client.send_binary = MagicMock()
    #     client._ws_client.send = MagicMock()

    #     # start evil stream
    #     client.start_stream(media_generator=evil_media_gen())

    #     # assert we get the expected exception
    #     time.sleep(0.01)
    #     client._on_media_error.assert_called_with(ex)

    # def test_bad_media_generator(self):

    #     # init client
    #     client = SpeechStreamClient(access_token=self.access_token, stream_id=self.stream_id, on_media_error=MagicMock())
    #     self._patch_client(client)

    #     # invalid media generator
    #     invalid_media_generator = range(10)

    #     # start (invalid) stream
    #     client.start_stream(media_generator=invalid_media_generator)

    #     # assert we get a type error from media sending thread
    #     time.sleep(0.01)
    #     client._on_media_error.assert_called_once()
    #     first_call_arg = client._on_media_error.call_args[0][0]
    #     self.assertTrue(isinstance(first_call_arg, TypeError))

    # ======= #
    # Helpers #
    # ======= #
    def _test_close_common(self, close_msg):

        # mock websocket receive data func
        side_effect = [(websocket.ABNF.OPCODE_TEXT, RESPONSES['happy_json_resp0']),
                       (websocket.ABNF.OPCODE_CLOSE, close_msg)]
        self.client._ws_client.recv_data = MagicMock(side_effect=side_effect)

        # start streaming mocked media (and mock connection)
        response_generator = self.client.start_stream(media_generator=self.valid_media_generator)
        for i, response in enumerate(response_generator):
            self.assertEqual(response, self._json_to_dict(side_effect[i][1]))
            time.sleep(0.0001)  # sleep less than media streaming time

    @staticmethod
    def _fake_media_generator(num_samples, num_chunks=0, delay_sec=0.1):
        """Fake media, of 16 bits per sample binary data"""
        for _ in range(num_chunks):
            yield b'\xff\xf8' * num_samples
            time.sleep(delay_sec)

    @staticmethod
    def _patch_client(client):

        def mock_connect(*args, **kwargs):
            client._ws_client.connected = True
            return unittest.mock.DEFAULT

        def mock_send_binary(chunk):
            if not client._ws_client.connected:
                raise ConnectionError('Mocked disconnected ws.')

            # if chunk has no len (means it's not bytes) - this will raise an exception
            len(chunk)

            return unittest.mock.DEFAULT

        def mock_close(*args, **kwargs):
            client._ws_client.connected = False
            return unittest.mock.DEFAULT

        client._ws_client.connect = MagicMock(side_effect=mock_connect)
        client._ws_client.send_binary = MagicMock(side_effect=mock_send_binary)
        client._ws_client.send = MagicMock()
        client._ws_client.close = MagicMock(side_effect=mock_close)

    @staticmethod
    def _json_to_dict(j: bytes):
        return json.loads(j.decode('utf-8'))
