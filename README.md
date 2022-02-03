# Verbit Streaming Python SDK

## Purpose

This package is a Python SDK for Verbit's Streaming Transcription API.
It can also be used as a reference implementation for porting to other programming languages.
You can use it as-is (see installation instructions below), or use it as
an example for implementing your own custom client.

The packages includes a Python client for streaming media and getting responses from Verbit's
Speech Recognition services via WebSocket connection.

You can use it as-is (see installation instructions below), or use it as
a Python implementation example, and implement the client yourself.


## Documentation

See our [API docs](https://www.XXXX.ai/docs) for more information about the API and
more python examples.

## Installation

To install this package simply run:  ***TODO : Decide on package name***

    pip install --upgrade verbit-streaming-sdk

Install from source with:

    python setup.py install

### Requirements

- Python 3.8+  ***TODO : We can easily reduce this requirement to Python 3.6***

## Usage

To start using the client, you will need an Access Token, which is currently
generated by our [Booking System](https://www.link-to-booking.co).

Once Create a client with the
generated Access Token:

```example_create_client.py
from verbit.streaming_client import SpeechStreamClient

client = SpeechStreamClient(access_token="ACCESS TOKEN")
```

### Streamed audio and responses:

Create a generator function yielding audio chunks of type `byte` in order to provide an audio-stream to the client-SDK.

Current SDK version only supports 16-bit signed-little-endian PCM input from this generator.

The following example streams audio from a PCM-`wave` file:

```example_stream_wav.py
from time import sleep
from verbit.streaming_client import SpeechStreamClient

CHUNK_DURATION_SECONDS = 0.1
AUDIO_FILENAME = 'example.wav'

def media_generator_wavefile(filename, chunk_duration):
    """
    Example generator, for streaming a 'WAV' audio-file, simulating realtime playback-rate using sleep()
    """

    # calculate chunk size
    # Note: assuming input file is a 16-bit mono 16000Hz WAV file
    chunk_size = int(chunk_duration * 2 * 16000)

    with open(filename, 'rb') as wav:
        while chunk_bytes := wav.read(chunk_size):
            yield chunk_bytes
            sleep(chunk_duration)

media_generator = media_generator_wavefile( AUDIO_FILENAME, CHUNK_DURATION_SECONDS)

client = SpeechStreamClient(access_token="ACCESS TOKEN")

response_generator = client.start_stream(media_generator=media_generator,
                                         media_config=MediaConfig(format='S16LE',     # signed 16-bit little-endian PCM
                                                                  sample_rate=16000,  # in Hz
                                                                  sample_width=2))    # in bytes
```

The resulting `response_generator` is a generator-function provided by the SDK for the client application to consume responses from.

```example_stream_wav.py
# get transcription responses
print('Listening for responses ...')
for response in response_generator:
    alternatives = response['response']['alternatives']
    alt0_transcript = alternatives[0]['transcript']
    print(alt0_transcript)
```

### Response format

[TODO: link to format]

### Response Types

The response has a `type` field, which is in (`transcript`, `captions`).

All response types have the same format.

1. Transcript: This is online transcription, the timestamps might overlap in different transcript responses, and the response has a boolean field `is_final`. The `alternatives` array has the difference hypotheses.

1. Captions: Non-overlapping consecutive responses. The `is_final` field is always `true` here, and the `alternatives` array has only one hypothesis.

### MediaConfig

TBD!

```python
class MediaConfig:
    format: str = 'S16LE'       # signed 16-bit little-endian PCM
    sample_rate: int = 16000    # in Hz
    sample_width: int = 2       # in bytes
    num_channels: int = 1
```
### Running tests:
```
pip install -r requirements_dev.txt  # install pytest et al.
pytest
```

----
End of file.