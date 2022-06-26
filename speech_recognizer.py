#!/usr/bin/env python3

"""
Usage:
    speech_recognizer.py azure --azure-speech-key=<azure_speech_key> [--azure-service-region=<azure_service_region>] [--phrases-file=<phrases_file>] <wave_filename>
    speech_recognizer.py gcp <wave_filename>

Options:
    -h --help    show this
    --phrases-file=<phrases_file>  File path for phrases to emphasize
    --azurespeechkey=<azure_speech_key>  Azure speech key
    --azureserviceregion=<azure_service_region>  Azure service region [default: westus]
"""

from docopt import docopt
import time
import re
from scipy.io import wavfile
import azure.cognitiveservices.speech as speechsdk
from typing import List

WAVE_CHANNELS = 2
WAVE_BPS = 16
WAVE_SPS = 44100

LANGUAGE_CODE_JAPANESE = "ja-JP"

CSV_HEADER = "start_ms,end_ms,start_tc,end_tc,is_estimated_start,is_estimated_end,display_text"

TIME_ONE_SECOND = 1000
TIME_ONE_MINUTE = TIME_ONE_SECOND * 60
TIME_ONE_HOUR = TIME_ONE_MINUTE * 60


def convert_to_timecode(source_ms: int) -> str:
    h = source_ms // TIME_ONE_HOUR
    m = (source_ms % TIME_ONE_HOUR) // TIME_ONE_MINUTE
    s = (source_ms % TIME_ONE_MINUTE) // TIME_ONE_SECOND
    ms = (source_ms % TIME_ONE_SECOND)
    return "%02d:%02d:%02d:%03d" % (h, m, s, ms)


def print_csv_line(start_ms: int, end_ms: int, is_estimated_start: bool, is_estimated_end: bool, sentence: str):
    start_tc = convert_to_timecode(start_ms)
    end_tc = convert_to_timecode(end_ms)

    print(f'{start_ms},{end_ms},"{start_tc}","{end_tc}",{is_estimated_start},{is_estimated_end},{sentence}')


class AzureRecognizer:
    AZURE_SEGMENT_BREAK_MS = 100
    AZURE_MSEC = 10 ** 4

    def __init__(self, speech_key: str, service_region: str) -> None:
        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
        speech_config.enable_dictation()

        wave_format = speechsdk.audio.AudioStreamFormat(WAVE_SPS, WAVE_BPS, WAVE_CHANNELS)
        self.stream = speechsdk.audio.PushAudioInputStream(stream_format=wave_format)
        audio_config = speechsdk.audio.AudioConfig(stream=self.stream)

        self.speech_recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config,
            language=LANGUAGE_CODE_JAPANESE,
            audio_config=audio_config,
        )

        self.speech_recognizer.recognized.connect(self._cb_recognized)
        self.speech_recognizer.session_stopped.connect(self._cb_stop)
        self.speech_recognizer.canceled.connect(self._cb_stop)

        self.phrase_list = speechsdk.PhraseListGrammar.from_recognizer(self.speech_recognizer)

        self.done = False
        self.results: List[speechsdk.SpeechRecognitionResult] = list()

    def add_phrase(self, phrase: str) -> None:
        self.phrase_list.addPhrase(phrase)

    def _cb_recognized(self, event: speechsdk.SpeechRecognitionEventArgs) -> None:
        self.results.append(event.result)

    def _cb_stop(self, event: speechsdk.SessionEventArgs) -> None:
        self.done = True

    def start_recognition(self, wave_file_name: str) -> None:
        self.speech_recognizer.start_continuous_recognition()

        _, wav_data = wavfile.read(wave_file_name)
        self.stream.write(wav_data.tobytes())
        self.stream.close()

    def stop_recognition(self) -> None:
        self.speech_recognizer.stop_continuous_recognition()

    def print_result_csv(self):
        if not self.done:
            print("recognition not finished")
            return

        print(CSV_HEADER)

        for result in self.results:
            segment_start = result.offset // self.AZURE_MSEC
            segment_duration = result.duration // self.AZURE_MSEC
            segment_end = segment_start + segment_duration

            display_text = result.text
            sentences = list(filter(lambda x: len(x) > 0, re.split("。|？", display_text)))

            if len(sentences) <= 1:
                if len(sentences) == 1:
                    print_csv_line(segment_start, segment_end, False, False, display_text)
                continue

            num_chars = sum(len(s) for s in sentences)

            sentence_i = 0
            sentence_start = segment_start
            for j, sentence in enumerate(sentences):
                sentence_i = display_text.find(sentence, sentence_i)
                sentence_display_text = display_text[sentence_i:sentence_i + len(sentence) + 1]
                sentence_i = sentence_i + len(sentence) + 1

                sentence_duration_esimation = \
                    int((segment_duration - self.AZURE_SEGMENT_BREAK_MS * (len(sentences) - 1)) * len(sentence) / num_chars)
                if j == len(sentences) - 1:
                    sentence_duration_esimation = segment_end - sentence_start

                print_csv_line(sentence_start, sentence_start + sentence_duration_esimation, j == 0, j == len(sentences) - 1, sentence_display_text)

                sentence_start += sentence_duration_esimation + self.AZURE_SEGMENT_BREAK_MS


if __name__ == '__main__':
    arguments = docopt(__doc__)
    phrases: List[str] = list()

    if arguments["--phrases-file"]:
        phrases_file = open(arguments["--phrases-file"], "r")
        phrases = list(map(lambda x: x.strip(), phrases_file.readlines()))
        phrases_file.close()

    if arguments['azure']:
        azure_speech_key = arguments['--azure-speech-key']
        azure_service_region = arguments['--azure-service-region'] if arguments['--azure-service-region'] else 'westus'

        recognizer = AzureRecognizer(azure_speech_key, azure_service_region)

        for phrase in phrases:
            recognizer.add_phrase(phrase)

        recognizer.start_recognition(arguments['<wave_filename>'])

        while not recognizer.done:
            time.sleep(1)

        recognizer.print_result_csv()
