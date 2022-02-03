import json
import unittest
import websocket
import pkg_resources
from os import path
from unittest.mock import MagicMock, patch

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

# Test covering 'example_client.py':

# helper Mocks to cover the 'example_client':
def mock_connect_ok_with_sideeffect(self, *args, **kwargs):
    self.connected = True
    # return unittest.mock.DEFAULT


def mock_close_with_sideeffect(self, *args, **kwargs):
        self.connected = False


ws_replies_side_effect = [(websocket.ABNF.OPCODE_TEXT, RESPONSES['happy_json_resp0']),
                          (websocket.ABNF.OPCODE_TEXT, RESPONSES['happy_json_resp1']),
                          (websocket.ABNF.OPCODE_TEXT, RESPONSES['happy_json_resp_EOS'])]


g_connection_fail_call_count = 0
REJECT_CONNECTION_COUNT = 2


def mock_connect_after_rejections(self, *args, **kwargs):
    """Mock: Reject connections N times, then accept."""
    global g_connection_fail_call_count
    g_connection_fail_call_count += 1
    # return unittest.mock.DEFAULT
    if g_connection_fail_call_count <= REJECT_CONNECTION_COUNT:
        raise websocket.WebSocketException("Connection rejected by mocking")
    self.connected = True


def mock_start_stream(self, media_generator):
    def mocked_responses():
        for i in range(3):
            resp_bytes = RESPONSES['happy_json_resp0']
            resp = json.loads(resp_bytes.decode('utf-8'))
            yield resp
    return mocked_responses()


class TestExampleClient(unittest.TestCase):

    def setUp(self):

        self.access_token = "fake-token"
        self.media_path = path.join('tests', 'resources', 'happy_json_resp0.json')
        # self.media_path = path.join('tests', 'resources', 'example.wav' . # ^ XXX: WARNING: we need a real `wav` file for other things to pass in the near future. + this is ugly.

    @patch('verbit.streaming_client.SpeechStreamClient.start_stream', mock_start_stream)
    def test_example_client_mocked_streams(self):
        example_client.example_streaming_client(self.access_token, self.media_path)
        # completion with no exception

    @patch('websocket.WebSocket.connect', mock_connect_ok_with_sideeffect)
    @patch('websocket.WebSocket.send_binary', MagicMock)
    @patch('websocket.WebSocket.send', MagicMock)
    @patch('websocket.WebSocket.close', mock_close_with_sideeffect)
    @patch('websocket.WebSocket.recv_data', MagicMock(side_effect=ws_replies_side_effect))
    def test_example_client_mocked_ws(self):
        example_client.example_streaming_client(self.access_token, self.media_path)
        # completion with no exception

    @patch('websocket.WebSocket.connect', mock_connect_after_rejections)
    @patch('websocket.WebSocket.send_binary', MagicMock)
    @patch('websocket.WebSocket.send', MagicMock)
    @patch('websocket.WebSocket.close', mock_close_with_sideeffect)
    @patch('websocket.WebSocket.recv_data', MagicMock(side_effect=ws_replies_side_effect))
    def test_example_ws_retry_and_connect(self):
        example_client.example_streaming_client(self.access_token, self.media_path)
        # completion with no exception

