#!/usr/bin/env python3

import argparse
from time import sleep
from pathlib import Path

from verbit.streaming_client import WebSocketStreamingClient

# constants
CHUNK_DURATION_SECONDS = 0.1

# set access token
streaming_access_token = '<your_access_token>'


def media_generator_wavefile(wav_path, chunk_duration):
    """
    Example generator, for streaming a 'WAV' audio-file, simulating realtime playback-rate using sleep()
    """

    # calculate chunk size
    # Note: assuming input file is a 16-bit mono 16000Hz PCM Wave file
    chunk_size = int(chunk_duration * 2 * 16000)

    with open(str(wav_path), 'rb') as wav:
        while chunk_bytes := wav.read(chunk_size):
            yield chunk_bytes
            sleep(chunk_duration)


def example_streaming_client(access_token, media_generator):

    # init verbit streaming client
    client = WebSocketStreamingClient(access_token=access_token)

    # upgrade connection to websocket and start audio stream
    response_generator = client.start_stream(media_generator=media_generator)

    # get transcription responses
    for response in response_generator:
        alternatives = response['response']['alternatives']
        alt0_transcript = alternatives[0]['transcript']
        print(alt0_transcript)


if __name__ == '__main__':

    # read command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--media_path', required=True, type=Path, help='Full path of the media file to stream')
    args = parser.parse_args()

    # init media chunks generator
    wav_media_generator = media_generator_wavefile(args.media_path, CHUNK_DURATION_SECONDS)

    # run example client
    example_streaming_client(streaming_access_token, wav_media_generator)
