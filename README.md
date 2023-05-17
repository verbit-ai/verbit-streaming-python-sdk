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

### Verbit API key
To access Verbit's Streaming Speech Recognition services an API key (customer token) should be obtained by sending an email request to the following address: api@verbit.ai  

### Ordering API
In order to use Verbit's Streaming Speech Recognition services, you must place an order using Verbit's Ordering API. Your request to the Ordering API must specify that the desired input and/or output schemes are streaming through a WebSocket. Upon successful placement of the order, you will be issued a WebScoket URL, composed of the base streaming API URL and your order's token. The URL, together with the customer token, will be used to initiate a WebSocket connection.

These two APIs and their respective SDKs are separated on purpose because placing orders to Verbit's Transcription services does not necessarily imply media streaming (you might want to upload a file instead).
Also, the services which operate order placement and the actual streaming of media are commonly distinct, therefore we find it useful to separate the SDKs to allow maximal flexibility for our customers.

For further details regarding the Ordering API, please refer to the documentation here: [Ordering API](https://app.swaggerhub.com/apis-docs/Verbit/ordering/).

### Creating a WebSocketStreamingClient

Create the client, and pass in the `Customer Token` as detailed above:

```python
from verbit.streaming_client import WebSocketStreamingClient

client = WebSocketStreamingClient(customer_token="CUSTOMER TOKEN")
```

### Streaming media via WebSocket

Create a generator function which yields chunks of audio (objects supporting the `bytes-like` interface).
The `WebSocketStreamingClient` will use your generator as input, iterating it and sending each audio chunk to the Speech Recognition service.

**Important: The Speech Recognition service expects the audio chunks to arrive at a realtime pace, or slower. Faster than realtime pace may cause the service to behave unexpectedly.**


#### Example

The following example reads audio from a WAV file and streams it to the Speech Recognition Service (Note: the example assumes that the customer token and WebSocket URL have been obtained via their respective API calls):

```python
import wave
from math import ceil
from time import sleep
from verbit.streaming_client import WebSocketStreamingClient, MediaConfig, ResponseType

CHUNK_DURATION_SECONDS = 0.1
AUDIO_FILENAME = 'example.wav'

def media_generator_wavefile(filename, chunk_duration):
    """
    Example generator, for streaming a 'WAV' audio-file, simulating realtime playback-rate using sleep()
    """

    with wave.open(str(filename), 'rb') as wav:
        nchannels, samplewidth, sample_rate, nframes, _, _ = wav.getparams()
        samples_per_chunk = ceil(chunk_duration * sample_rate)
        chunk_bytes = wav.readframes(samples_per_chunk)
        while chunk_bytes:
            yield chunk_bytes
            chunk_bytes = wav.readframes(samples_per_chunk)
            sleep(chunk_duration)

media_generator = media_generator_wavefile(AUDIO_FILENAME, CHUNK_DURATION_SECONDS)

media_config = MediaConfig(format='S16LE',      # signed 16-bit little-endian PCM
                           num_channels=1,      # number of audio channels
                           sample_rate=16000,   # in Hz
                           sample_width=2)      # in bytes

response_types = ResponseType.Transcript | ResponseType.Captions
    
client = WebSocketStreamingClient(customer_token="CUSTOMER TOKEN")

response_generator = client.start_stream(
   ws_url="WEBSOCKET URL",
   media_generator=media_generator,
   media_config=media_config,
   response_types=response_types)
```

### Providing media via an external source

It is possible to use an external media source to provide media to the Speech Recognition Service.
To do so, you need to specify the relevant input method when booking the session via Verbit's Ordering API.

In such a scenario, you should **not** provide a media generator to the `WebSocketStreamingClient`. 
Connecting the `WebSocketStreamingClient` to the Speech Recognition Service will initiate the session
and signal the server to start consuming media from the external media source.
Therefore, **you should only connect the `WebSocketStreamingClient` to the service after the external media source is ready.**

#### Example

The following example connects to the Speech Recognition Service without providing a media generator:

```python
from verbit.streaming_client import WebSocketStreamingClient, ResponseType

response_types = ResponseType.Transcript | ResponseType.Captions
    
client = WebSocketStreamingClient(customer_token="CUSTOMER TOKEN")

response_generator = client.start_with_external_source(ws_url="WEBSOCKET URL", response_types=response_types)
```


### Getting responses

The client's `start_stream()` and `start_with_external_source()` methods return a generator which can be iterated to fetch the Speech Recognition responses:
```python
# get recognition responses
print('Waiting for responses ...')
for response in response_generator:
    resp_type = response['response']['type']
    alternatives = response['response']['alternatives']
    alt0_transcript = alternatives[0]['transcript']
    print(f'{resp_type}: {alt0_transcript}')
```

#### End of Stream
When the media generator is exhausted, the client sends an End-of-Stream (non-binary) message to the service.

In a scenario where the media is coming from an external source, it is the user's responsibility to send the End-of-Stream message to the service.

The End-of-Stream message can be sent using the `send_eos_event()` method which internally sends the following payload:
```
{
   "event": "EOS"
}
```

### Response Types

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

#### Responses on silent audio segments
It should be noted that "transcript" and "captions" responses behave differently when the audio being transcribed is silent:
* "transcript" responses are sent regardless of the audio content, in such a way that the entire audio duration is covered by "transcript" responses. In case of a silent audio segment, "transcript" responses will be sent with an empty word list, but with timestamps which mark the portion of the audio that was transcribed.
* "captions" responses are sent only when the speech recognition output contains words. In case of a silent audio segment, no "captions" responses will be sent, since a caption doesn't make sense without any words. Therefore, "captions" responses will not necessarily cover the entire audio duration (i.e. there may be "gaps" between "captions" responses). 

### Error handling and recovery

#### Initial connection
In case the WebSocket client fails to establish the initial connection with the service, e.g. due to temporary unavailability, 
it will perform exponential retry, up to [`max_connection_retry_seconds`](https://github.com/verbit-ai/verbit-streaming-python-sdk/blob/main/verbit/streaming_client.py#L108) (configurable).

#### During a session
In case the connection to the service is dropped during a session, the behavior of the WebSocket client will depend on the implementation chosen by the user.
This client SDK contains two implementations, which have the same interface, but differ in their error handling behavior:
1. `WebSocketStreamingClientSingleConnection` - the base implementation; does not attempt to reconnect in case the connection was dropped prematurely. It can be useful, for example, if you would like to implement your own connection error handling logic.
2. `WebSocketStreamingClient` - the default implementation; will attempt to reconnect in case the connection was closed prematurely, as many times as needed, until the final response is received (or some non-retryable error occurrs).

### Idle streams
In case the media stream comes from an external source (e.g. RTMP), there may be times when no messages are sent over the WebSocket. 
For example:
* The external media source hasn't started yet
* The media stream is silent and only "captions" responses were requested (see section on [silent audio segments](https://github.com/verbit-ai/verbit-streaming-python-sdk/blob/main/README.md#responses-on-silent-audio-segments)). 

In case no message is sent over the WebSocket for more than 10 minutes, the connection will be dropped, and will need to be re-established. To prevent these undesired disconnections, it is advised to send a "ping" message at least once every 10 minutes. This client SDK sends a "ping" message every 1 minute, as long as the Websocket is connected. 

If you choose to implement your own client, make sure to handle the "pong" messages you will get from the service, in response to your "ping" messages. 

### Connection duration limit
In case the media stream comes from an external source (e.g. RTMP), the maximum allowed connection duration is 2 hours. After that time, the server will drop the connection with a "Going Away" (code: 1001) close message. In such cases, it is the client's responsibility to reconnect. 
This client SDK automatically attempts to reconnect if connection is closed with "Going Away" message.    

### Testing
This client SDK comes with a set of unit-tests that can be used to ensure the correct functionality of the streaming client.

To run the unit-tests:
```bash
pip install pytest
pip install -r tests/requirements_test.txt
pytest
```
