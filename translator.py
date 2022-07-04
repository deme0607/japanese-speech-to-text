#!/usr/bin/env python3

"""
Usage:
    translator.py translate --auth-key=<auth_key> <csv_filename>

Options:
    -h --help    show this
    --auth-key=<auth_key>  DeepL API key
"""

from docopt import docopt
import deepl
import csv
from typing import List

from speech_recognizer import LANGUAGE_CODE_JAPANESE


class DeepLTranslator:
    BATCH_SIZE = 50
    LANGUAGE_CODE_JAPANESE = "JA"
    LANGUAGE_CODE_ENGLISH = "EN-US"

    def __init__(self, auth_key: str) -> None:
        self.translator = deepl.Translator(auth_key)

    def translate_text(self, text: List[str]) -> List[str]:
        api_res: List[deepl.translator.TextResult] =\
            self.translator.translate_text(text, source_lang=self.LANGUAGE_CODE_JAPANESE, target_lang=self.LANGUAGE_CODE_ENGLISH)

        return list(map(lambda r: r.text, api_res))

    def print_csv(self, original_row: List[List[str]], translation: List[str]):
        for o, t in zip(original_row, translation):
            o.append(f'"{t}"')
            print(",".join(o))

    def translate_csv(self, csv_filename: str):
        with open(csv_filename) as csvfile:
            reader = csv.reader(csvfile)
            batch: List[List[str]] = list()

            for row in reader:
                batch.append(row)

                if len(batch) == self.BATCH_SIZE:
                    translated = self.translate_text(map(lambda r: r[-1], batch))
                    self.print_csv(batch, translated)
                    batch = list()

            if batch:
                translated = self.translate_text(map(lambda r: r[-1], batch))
                self.print_csv(batch, translated)


if __name__ == "__main__":
    arguments = docopt(__doc__)
    api_key = arguments["--auth-key"]
    csv_filename = arguments["<csv_filename>"]

    translator = DeepLTranslator(api_key)
    translator.translate_csv(csv_filename)
