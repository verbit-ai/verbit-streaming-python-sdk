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

In order to start using the service, you will need an Access Token which is generated by Verbit's Ordering API.
Please refer to documentation here: [Ordering API](https://app.swaggerhub.com/apis-docs/Verbit/Transcript/0.8#).

Create the client, and pass in the `Access Token` acquired from Ordering API:

```example_create_client.py
from verbit.streaming_client import SpeechStreamClient

client = SpeechStreamClient(access_token="ACCESS TOKEN")
```

### Streamed audio and responses:

Create a generator function which yields chunks of audio (objects supporting the `bytes-like` interface).
The StreamingClient will use your generator as input, iterating it and sending each audio chunk to the Speech Recognition service.

Note:
The current version of the service supports only WAV format (pcm_s16le - PCM signed 16-bit little-endian).
Your generator should output audio chunks containing this format, you may also include WAV headers.

The following example reads audio from a WAV file and streams it to the Speech Recognition service:

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

The client's `start_stream()` function returns a generator which can be iterated to fetch the results:
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

1. Transcript: This type of response contains the recognized words since the beginning of the current utterance. Like in real human speech, the stream of words is segmented into utterances in automatic speech recognition. An utterance is recognized incrementally, processing more of the incoming audio at each step. Each utterance starts at a specific start-time and extends its end-time with each step, yielding the most updated result.
Note that sequential updates for the same utterance will overlap, each response superseding the previous one - until a response signaling the end of the utterance is received (having `is_final == True`). 
The `alternatives` array might contain different hypotheses, however the 1st alternative is commonly what you're looking for.

2. Captions: This type of response contains the recognized within a specific time window. In contrast to the incremental nature of "transcript"-type responses, these "captions"-type responses are non-overlapping and consecutive. You will only get one response covering a specific time span in the audio (or none, if no words were uttered). 
The `is_final` field is always `True` because no updates will be output. And the `alternatives` array always has only one item.
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
pip install pytest
pip install -r tests/requirements_test.txt
pytest
```

----
End of file.