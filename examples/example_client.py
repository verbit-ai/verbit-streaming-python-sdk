#!/usr/bin/env python3

import argparse
from time import sleep
from pathlib import Path

from verbit.streaming_client import SpeechStreamClient

# constants
CHUNK_DURATION_SECONDS = 0.1

# set access token
access_token = '<your-access-token>'

def media_generator_wavefile(wav_path, chunk_duration):
    """
    Example generator, for streaming a 'WAV' audio-file, simulating realtime playback-rate using sleep()
    """

    # calculate chunk duration
    # Note: assuming input file is a 16-bit mono 16000Hz WAV file
    chunk_size = int(chunk_duration * 16000)
    # ^ BUGFIX: just tested: wav.read() reads 'frames' where a PCM 'frame' - is a sample, which is already 'samplewidth' (2) bytes

    with open(str(wav_path), 'rb') as wav:
        while chunk_bytes := wav.read(chunk_size):
            yield chunk_bytes
            sleep(chunk_duration)


def example_streaming_client(access_token, media_path):
    # init verbit streaming client
    client = SpeechStreamClient(access_token=access_token)

    # init media chunks generator
    media_generator = media_generator_wavefile(media_path,
                                               CHUNK_DURATION_SECONDS)

    # upgrade connection to websocket and start audio stream
    print('Connecting ...')
    response_generator = client.start_stream(media_generator=media_generator)
    print('Connected!')

    # get transcription responses
    print('Listening for responses ...')
    for response in response_generator:
        alternatives = response['response']['alternatives']
        alt0_transcript = alternatives[0]['transcript']
        print(alt0_transcript)


if __name__ == '__main__':

    # read command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-m',
                        '--media_path',
                        required=True,
                        type=Path,
                        help='Full path of the media file to stream')
    args = parser.parse_args()

    example_streaming_client(access_token, args.media_path)

