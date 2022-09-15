#!/usr/bin/env python3

import wave
import argparse
from math import ceil
from time import sleep
from pathlib import Path

from verbit.streaming_client import WebSocketStreamingClient, MediaConfig, ResponseType

# constants
CHUNK_DURATION_SECONDS = 0.1

# set token and url
example_customer_token = '<your_customer_token>'
example_ws_url = '<websocket_url>'  # should include 'token' query parameter.


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


def example_streaming_client(ws_url, customer_token, media_generator):

    # init verbit streaming client
    client = WebSocketStreamingClient(customer_token)

    # set the properties of the media to be sent by the client
    media_config = MediaConfig(format='S16LE',        # signed 16-bit little-endian PCM
                               num_channels=1,      # number of audio channels
                               sample_rate=16000,   # in Hz
                               sample_width=2)      # in bytes

    # set response types to request from the service
    response_types = ResponseType.Transcript | ResponseType.Captions

    # upgrade connection to websocket and start audio stream
    response_generator = client.start_stream(ws_url, media_generator=media_generator, media_config=media_config, response_types=response_types)

    # get transcription responses
    for response in response_generator:
        resp_type = response['response']['type']
        alternatives = response['response']['alternatives']
        alt0_transcript = alternatives[0]['transcript']
        print(f'{resp_type}: {alt0_transcript}')


if __name__ == '__main__':

    # read command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--media_path', required=True, type=Path, help='Full path of the media file to stream')
    args = parser.parse_args()

    # init media chunks generator
    wav_media_generator = media_generator_wavefile(args.media_path, CHUNK_DURATION_SECONDS)

    # run example client
    example_streaming_client(example_ws_url, example_customer_token, wav_media_generator)
