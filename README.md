# Japanese Speech-to-Text

Set up Python scripts to generate an SRT (SubRip Subtitle) file in English from Japanese audio.

## Install

```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

### Generate Japanese subtitle as a CSV

```
# Use Microsoft Azure Cognitive Services Speech-to-text
./speech_recognizer.py azure --azure-speech-key={AZURE_SPEECH_KEY} data/{JAPANESE_AUDIO_FILE.wav} > data/result.csv

# Use Google Cloud Text-to-Speech
./speech_recognizer.py gcp gs://{GCS_FILE_PATH.wav} > data/result.csv
```

### Generate English translation from Japanese subtitle CSV

```
./translator.py translate --auth-key={DEEPL_AUTH_KEY} data/{JAPANESE_SUBTITLE_FILE.csv}
```

### Validate timecode

```
./csv_validator.py validate data/{SUBTITLE_FILE.csv}
```
