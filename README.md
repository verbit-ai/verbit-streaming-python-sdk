# Verbit Streaming Python SDK

## Overview

This package is a Python SDK for Verbit's Streaming Transcription API.
It can also be used as a reference implementation for porting to other programming languages.
You can use it as-is (see installation instructions below), or use it as an example for implementing your own custom client.

The package includes a Python client for streaming media and getting responses from Verbit's Streaming Speech Recognition services via a WebSocket connection.

## Installation

To install this package run:

    pip install --upgrade verbit-streaming-sdk

### Requirements

- Python 3.8+

## Usage

### Ordering API
In order to use Verbit's Streaming Speech Recognition services, you must place an order using Verbit's Ordering API. Your request to the Ordering API must specify that the desired input and output schemes are streaming through a WebSocket. Upon successful placement of the order, you will be issued an authentication token which can be used to initiate a WebSocket connection.

These two APIs and their respective SDKs are separated on purpose because placing orders to Verbit's Transcription services does not necessarily imply media streaming (you might want to upload a file instead).
Also, the services which operate order placement and the actual streaming of media are commonly distinct, therefore we find it useful to separate the SDKs to allow maximal flexibility for our customers.

Please refer to our documentation here: [Ordering API](https://platform.verbit.co/api_docs).

### Streaming audio and getting responses

Create the client, and pass in the `Access Token` acquired from the Ordering API:

```python
from verbit.streaming_client import WebSocketStreamingClient

client = WebSocketStreamingClient(access_token="ACCESS TOKEN")
```

Create a generator function which yields chunks of audio (objects supporting the `bytes-like` interface).
The StreamingClient will use your generator as input, iterating it and sending each audio chunk to the Speech Recognition service.

_Note:
The current version of the service supports only WAV format (pcm_s16le - PCM signed 16-bit little-endian).
Your generator should output audio chunks containing this format, which may also include WAV headers._

### Example

The following example reads audio from a WAV file and streams it to the Speech Recognition service:

```python
from time import sleep
from verbit.streaming_client import WebSocketStreamingClient

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

client = WebSocketStreamingClient(access_token="ACCESS TOKEN")

response_generator = client.start_stream(media_generator=media_generator,
                                         media_config=MediaConfig(format='S16LE',     # signed 16-bit little-endian PCM
                                                                  sample_rate=16000,  # in Hz
                                                                  sample_width=2))    # in bytes
```

The client's `start_stream()` function returns a generator which can be iterated to fetch the Speech Recognition responses:
```python
# get recognition responses
print('Waiting for responses ...')
for response in response_generator:
    alternatives = response['response']['alternatives']
    alt0_transcript = alternatives[0]['transcript']
    print(alt0_transcript)
```


### Responses

Responses received through the WebSocket are JSON objects with a specific schema (a full description of which can be found in [examples/responses/schema.md](https://github.com/verbit-ai/verbit-streaming-python-sdk/blob/main/examples/responses/schema.md)).
There are two types of responses - "transcript" and "captions":

1. **Transcript**: this type of response contains the recognized words since the beginning of the current utterance. Like in real human speech, the stream of words is segmented into utterances in automatic speech recognition. An utterance is recognized incrementally, processing more of the incoming audio at each step. Each utterance starts at a specific start-time and extends its end-time with each step, yielding the most updated result.
Note that sequential updates for the same utterance will overlap, each response superseding the previous one - until a response signaling the end of the utterance is received (having `is_final == True`).
The `alternatives` array might contain different hypotheses, ordered by confidence level.

    Example "transcript" responses can be found in [examples/responses/transcript.md](https://github.com/verbit-ai/verbit-streaming-python-sdk/blob/main/examples/responses/transcript.md).


2. **Captions**: this type of response contains the recognized words within a specific time window. In contrast to the incremental nature of "transcript"-type responses, the "captions"-type responses are non-overlapping and consecutive. 
Only one "captions"-type response covering a specific time-span in the audio will be returned (or none, if no words were uttered).
The `is_final` field is always `True` because no updates will be output for the same time-span. The `alternatives` array will always have only one item for captions.

    Example "captions" responses can be found in [examples/responses/captions.md](https://github.com/verbit-ai/verbit-streaming-python-sdk/blob/main/examples/responses/captions.md).

### Testing
This client SDK comes with a set of unit-tests that can be used to ensure the correct functionality of the streaming client.

To run the unit-tests:
```bash
pip install pytest
pip install -r tests/requirements_test.txt
pytest
```
