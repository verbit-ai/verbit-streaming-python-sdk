
import pkg_resources
from os import path


# Load test resources:
def _load_json_resource(name):
    rel_path = pkg_resources.resource_filename(__name__, path.join('resources', name + '.json'))
    with open(rel_path, 'rb') as f:
        json_bytes = f.read()
    return json_bytes


# init mock responses
RESOURCE_KEYS = ['happy_json_resp0', 'happy_json_resp1', 'happy_json_resp_EOS']
RESPONSES = {k: _load_json_resource(k) for k in RESOURCE_KEYS}


def mock_get_auth_token(_self, *_args, **_kwargs):
    return "fake-auth-token"
