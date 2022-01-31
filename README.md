# Verbit Streaming Python SDK

***TODO : 'CI Badge'***
(badge fails, while repo is private for now, and no CI has been set up)
[![CIRCLE-CI::verbit-ai](https://circleci.com/gh/verbit-ai/verbit-streaming-python-sdk/tree/master.svg?style=shield)](https://app.circleci.com/pipelines/github/verbit-ai/verbit-streaming-python-sdk)

[comment: Or Github Actions setup..]

Example: `Pylon` (with private API-token:status-only, since repo is private)

* branch: `master`
[![verbit-ai](https://circleci.com/gh/verbit-ai/pylon/tree/master.svg?style=shield&circle-token=de6a837438fb7efc31b8cb857b9304b0b1f0c09c)](https://app.circleci.com/pipelines/github/verbit-ai/pylon)

 * branch: `none-existing`
[![verbit-ai](https://circleci.com/gh/verbit-ai/pylon/tree/none-existing.svg?style=shield&circle-token=de6a837438fb7efc31b8cb857b9304b0b1f0c09c)](https://app.circleci.com/pipelines/github/verbit-ai/pylon)

  * branch: RND-13654-event-bridge-client-roy : style `shield` (older circle-ci style)
[![verbit-ai](https://circleci.com/gh/verbit-ai/pylon/tree/RND-13654-event-bridge-client-roy.svg?style=shield&circle-token=de6a837438fb7efc31b8cb857b9304b0b1f0c09c)](https://app.circleci.com/pipelines/github/verbit-ai/pylon)

 * or style: `svg` (new default on circle-CI)
   [![verbit-ai](https://circleci.com/gh/verbit-ai/pylon/tree/RND-13654-event-bridge-client-roy.svg?circle-token=de6a837438fb7efc31b8cb857b9304b0b1f0c09c)](https://app.circleci.com/pipelines/github/verbit-ai/pylon)

 * branch: `RND-13454-add-git-info-roy`
[![verbit-ai](https://circleci.com/gh/verbit-ai/pylon/tree/RND-13654-event-bridge-client-roy.svg?style=shield&circle-token=de6a837438fb7efc31b8cb857b9304b0b1f0c09c)](https://app.circleci.com/pipelines/github/verbit-ai/pylon)



## Purpose

This package is the __reference implementation__ for Verbit's Streaming API.

It is a client SDK for streaming media to, and getting responses from Verbit's
Speech Recognition services, via a standard WebSocket connection.

You can use it as-is (see installation instructions below), or use it as
a Python implementation example, and implement the client yourself.


## Documentation

See our [API docs](https://www.XXXX.ai/docs) for more information about the API and
more python examples.

## Installation

To install the package via PyPi simply run:  ***TODO : Decide on package name***

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

```python
from verbit.streaming_client import SpeechStreamClient

client = SpeechStreamClient(access_token="ACCESS TOKEN")
```

### Streamed audio and responses:

Create a generator function yielding audio chunks of type `byte` in order to provide an audio-stream to the client-SDK.

Current SDK version only supports 16-bit signed-little-endian PCM input from this generator.

The following example streams audio from a PCM-`wave` file:

```python
from time import sleep
from verbit.streaming_client import SpeechStreamClient

CHUNK_DURATION_SECONDS = 0.1
media_path = 'example.wav'

def media_generator_wavefile(wav_path, chunk_duration):
    """
    Example generator, for streaming a 'WAV' audio-file, simulating realtime playback-rate using sleep()
    """

    # calculate chunk size
    # Note: assuming input file is a 16-bit mono 16000Hz WAV file
    chunk_size = int(chunk_duration * 16000)

    with open(str(wav_path), 'rb') as wav:
        while chunk_bytes := wav.read(chunk_size):
            yield chunk_bytes
            sleep(chunk_duration)

media_generator = media_generator_wavefile(media_path, CHUNK_DURATION_SECONDS)

response_generator = client.start_stream(media_generator=media_generator)
```

The resulting `response_generator` is another generator-function provided by the SDK, for the client application to consume responses from. There are two types of responses: Captions and updating-transcriptions:
[WIP]
```python
# get transcription responses
print('Listening for responses ...')
for response in response_generator:
    alternatives = response['response']['alternatives']
    alt0_transcript = alternatives[0]['transcript']
    print(alt0_transcript)
```

----
End of file.