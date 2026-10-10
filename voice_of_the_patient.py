
import logging
import os
from io import BytesIO

import speech_recognition as sr
from pydub import AudioSegment
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

def record_audio(file_path, timeout=20, phrase_time_limit=10):
    """Record microphone audio and save it as MP3."""
    recognizer = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            logging.info("Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=1)

            logging.info("Start speaking now...")

            audio_data = recognizer.listen(
                source,
                timeout=timeout,
                phrase_time_limit=phrase_time_limit,
            )

        wav_data = audio_data.get_wav_data()
        audio_segment = AudioSegment.from_wav(BytesIO(wav_data))
        audio_segment.export(file_path, format="mp3", bitrate="128k")

        logging.info("Audio saved to %s", file_path)

    except sr.WaitTimeoutError:
        logging.warning("No speech detected before the timeout.")
        raise
    except OSError as exc:
        logging.error("Microphone or audio-device error: %s", exc)
        raise


def transcribe_patient_voice(audio_filepath):
    """Transcribe recorded audio using Groq Whisper."""
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError("GROQ_API_KEY is missing from .env")

    if not os.path.isfile(audio_filepath):
        raise FileNotFoundError(f"Audio file not found: {audio_filepath}")

    client = Groq(api_key=api_key)

    with open(audio_filepath, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            file=audio_file,
            model=os.getenv("WHISPER_MODEL", "whisper-large-v3"),
        )

    return transcription.text


if __name__ == "__main__":
    audio_filepath = "patient_voice_test.mp3"

    try:
        record_audio(
            audio_filepath,
            timeout=20,
            phrase_time_limit=10,
        )

        text = transcribe_patient_voice(audio_filepath)

        print("\nPatient transcription:")
        print(text)

    except sr.WaitTimeoutError:
        print("Recording timed out. Please try again.")
    except Exception as exc:
        logging.exception("Audio processing failed: %s", exc)

