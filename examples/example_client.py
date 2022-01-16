#!/usr/bin/env python3

import argparse
from time import sleep
from pathlib import Path

from verbit.streaming_client import SpeechStreamClient

# constants
CHUNK_DURATION_SECONDS = 0.1


def media_generator_wavefile(wav_path, chunk_duration):
    """
    Example generator, for streaming a 'WAV' audio-file, simulating realtime playback-rate using sleep()
    """

    # calculate chunk duration
    # Note: assuming input file is a 16-bit mono 16000Hz WAV file
    chunk_size = int(chunk_duration * 2 * 16000)

    with open(str(wav_path), 'rb') as wav:
        while chunk_bytes := wav.read(chunk_size):
            yield chunk_bytes
            sleep(chunk_duration)


if __name__ == '__main__':

    # read command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--media_path', required=True, type=Path, help='Full path of the media file to stream')
    args = parser.parse_args()

    # set access token
    access_token = 'secret!'

    # init verbit streaming client
    client = SpeechStreamClient(access_token=access_token)

    # init media chunks generator
    media_generator = media_generator_wavefile(args.media_path, CHUNK_DURATION_SECONDS)

    # upgrade connection to websocket and start audio stream
    print('Connecting ...')
    response_generator = client.start_stream(media_generator=media_generator)
    print('Connected!')

    # get transcription responses
    print('Listening for responses ...')
    for response in response_generator:
        print(response)
