# Test covering 'example_client.py':
import json
import struct
import unittest
import websocket
from unittest.mock import MagicMock, patch

from examples import example_client
from tests.common import RESPONSES, mock_get_auth_token

# globals
g_connection_fail_call_count = 0

# constants
REJECT_CONNECTION_COUNT = 2
HAPPY_CLOSE_MSG = struct.pack("!H", websocket.STATUS_GOING_AWAY) + b"Test generator ended is the reason."
WS_REPLIES_SIDE_EFFECT = [(websocket.ABNF.OPCODE_TEXT, RESPONSES['happy_json_resp0']),
                          (websocket.ABNF.OPCODE_TEXT, RESPONSES['happy_json_resp1']),
                          (websocket.ABNF.OPCODE_TEXT, RESPONSES['happy_json_resp_EOS']),
                          (websocket.ABNF.OPCODE_CLOSE, HAPPY_CLOSE_MSG)]


# Helper Mocks to cover the 'example_client':
def mock_connect_ok_with_sideeffect(_self, *_args, **_kwargs):
    _self.connected = True


def mock_close_with_sideeffect(_self, *_args, **_kwargs):
    _self.connected = False


def mock_connect_after_rejections(_self, *_args, **_kwargs):
    """Mock: Reject connections N times, then accept."""
    global g_connection_fail_call_count
    g_connection_fail_call_count += 1
    # return unittest.mock.DEFAULT
    if g_connection_fail_call_count <= REJECT_CONNECTION_COUNT:
        raise websocket.WebSocketException("Connection rejected by mocking")
    _self.connected = True


def mock_start_stream(_self, *_args, **_kwargs):
    def mocked_responses():
        for i in range(3):
            resp_bytes = RESPONSES['happy_json_resp0']
            resp = json.loads(resp_bytes.decode('utf-8'))
            yield resp
    return mocked_responses()


class TestExampleClient(unittest.TestCase):

    def setUp(self):

        self.customer_token = "fake-token"
        self.ws_url = "fake-ws-url"
        self.mock_media_gen = (b'\x01' for _ in range(2))

    @patch('verbit.streaming_client.WebSocketStreamingClient.start_stream', mock_start_stream)
    @patch('verbit.streaming_client.WebSocketStreamingClient._get_auth_token', mock_get_auth_token)
    def test_example_client_mocked_streams(self):
        example_client.example_streaming_client(self.ws_url, self.customer_token, self.mock_media_gen)
        # completion with no exception

    @patch('websocket.WebSocket.connect', mock_connect_ok_with_sideeffect)
    @patch('websocket.WebSocket.send_binary', MagicMock)
    @patch('websocket.WebSocket.send', MagicMock)
    @patch('websocket.WebSocket.close', mock_close_with_sideeffect)
    @patch('websocket.WebSocket.recv_data', MagicMock(side_effect=WS_REPLIES_SIDE_EFFECT))
    @patch('verbit.streaming_client.WebSocketStreamingClient._get_auth_token', mock_get_auth_token)
    def test_example_client_mocked_ws(self):
        example_client.example_streaming_client(self.ws_url, self.customer_token, self.mock_media_gen)
        # completion with no exception

    @patch('websocket.WebSocket.connect', mock_connect_after_rejections)
    @patch('websocket.WebSocket.send_binary', MagicMock)
    @patch('websocket.WebSocket.send', MagicMock)
    @patch('websocket.WebSocket.close', mock_close_with_sideeffect)
    @patch('websocket.WebSocket.recv_data', MagicMock(side_effect=WS_REPLIES_SIDE_EFFECT))
    @patch('verbit.streaming_client.WebSocketStreamingClient._get_auth_token', mock_get_auth_token)
    def test_example_ws_retry_and_connect(self):
        example_client.example_streaming_client(self.ws_url, self.customer_token, self.mock_media_gen)
        # completion with no exception

    # TODO: cover failures, reconnections, 502, 401 cases on connect
