#!/usr/bin/env python3

import wave
import argparse
from math import ceil
from time import sleep
from pathlib import Path

from verbit.streaming_client import SpeechStreamClient, MediaConfig

# constants
CHUNK_DURATION_SECONDS = 0.1


# Warning: Server only supports: mono, samplewidth == 2, signed-16-bit audio.
def media_generator_wavefile(media_path, chunk_seconds):
    """
    Example generator, for streaming a 'WAV' audio-file, simulating realtime playback-rate using sleep()
    """
    with wave.open(str(media_path), 'rb') as wav:
        nchannels, samplewidth, sample_rate, nframes, _, _ = wav.getparams()
        samples_per_chunk = ceil(chunk_seconds * sample_rate)
        chunk_bytes = wav.readframes(samples_per_chunk)
        while chunk_bytes:
            yield chunk_bytes
            chunk_bytes = wav.readframes(samples_per_chunk)
            sleep(chunk_seconds)


if __name__ == '__main__':

    # read command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--media_path', required=True, type=Path, help='Full path of the media file to stream')
    parser.add_argument('-s', '--stream_id', required=True, type=str, help='Stream ID obtained via booking a session')
    args = parser.parse_args()

    # set access token
    access_token = 'secret!'

    # init verbit streaming client
    client = SpeechStreamClient(access_token=access_token, stream_id=args.stream_id)

    # init media config
    media_config = MediaConfig(
        format='PCM',
        sample_rate=16000,
        sample_width=2,
        num_channels=1
    )

    # init media chunks generator
    media_generator = media_generator_wavefile(args.media_path, CHUNK_DURATION_SECONDS)

    # upgrade connection to websocket and start audio stream
    response_generator = client.start_stream(media_generator=media_generator)

    # get transcription responses
    for response in response_generator:
        print(response)
