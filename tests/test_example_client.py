# Test covering 'example_client.py':
import json
import struct
import unittest
import websocket
from os import path
from unittest.mock import MagicMock, patch

from examples import example_client
from tests.common import RESPONSES


# Test mock global test-variables:
g_connection_fail_call_count = 0

# Constants for mocks:
REJECT_CONNECTION_COUNT = 2


# Helper Mocks to cover the 'example_client':
def mock_connect_ok_with_sideeffect(self, *args, **kwargs):
    self.connected = True


def mock_close_with_sideeffect(self, *args, **kwargs):
    self.connected = False

HAPPY_CLOSE_MSG = struct.pack("!H", websocket.STATUS_GOING_AWAY) + b"Test generator ended is the reason."

ws_replies_side_effect = [(websocket.ABNF.OPCODE_TEXT, RESPONSES['happy_json_resp0']),
                          (websocket.ABNF.OPCODE_TEXT, RESPONSES['happy_json_resp1']),
                          (websocket.ABNF.OPCODE_TEXT, RESPONSES['happy_json_resp_EOS']),
                          (websocket.ABNF.OPCODE_CLOSE, HAPPY_CLOSE_MSG)
                         ]


def mock_connect_after_rejections(self, *args, **kwargs):
    """Mock: Reject connections N times, then accept."""
    global g_connection_fail_call_count
    g_connection_fail_call_count += 1
    # return unittest.mock.DEFAULT
    if g_connection_fail_call_count <= REJECT_CONNECTION_COUNT:
        raise websocket.WebSocketException("Connection rejected by mocking")
    self.connected = True


def mock_start_stream(self, media_generator, media_config, response_types):
    def mocked_responses():
        for i in range(3):
            resp_bytes = RESPONSES['happy_json_resp0']
            resp = json.loads(resp_bytes.decode('utf-8'))
            yield resp
    return mocked_responses()


class TestExampleClient(unittest.TestCase):

    def setUp(self):

        self.access_token = "fake-token"
        self.mock_media_gen = (b'\x01' for _ in range(2))

    @patch('verbit.streaming_client.WebSocketStreamingClient.start_stream', mock_start_stream)
    def test_example_client_mocked_streams(self):
        example_client.example_streaming_client(self.access_token, self.mock_media_gen)
        # completion with no exception

    @patch('websocket.WebSocket.connect', mock_connect_ok_with_sideeffect)
    @patch('websocket.WebSocket.send_binary', MagicMock)
    @patch('websocket.WebSocket.send', MagicMock)
    @patch('websocket.WebSocket.close', mock_close_with_sideeffect)
    @patch('websocket.WebSocket.recv_data', MagicMock(side_effect=ws_replies_side_effect))
    def test_example_client_mocked_ws(self):
        example_client.example_streaming_client(self.access_token, self.mock_media_gen)
        # completion with no exception

    @patch('websocket.WebSocket.connect', mock_connect_after_rejections)
    @patch('websocket.WebSocket.send_binary', MagicMock)
    @patch('websocket.WebSocket.send', MagicMock)
    @patch('websocket.WebSocket.close', mock_close_with_sideeffect)
    @patch('websocket.WebSocket.recv_data', MagicMock(side_effect=ws_replies_side_effect))
    def test_example_ws_retry_and_connect(self):
        example_client.example_streaming_client(self.access_token, self.mock_media_gen)
        # completion with no exception

    # TODO: cover failures, reconnections, 502, 401 cases on connect
