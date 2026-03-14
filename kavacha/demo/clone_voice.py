"""
KAVACHA Demo — Voice Clone Generator
Uses Coqui TTS (free, offline) to clone a voice for deepfake demo.
Install: pip install TTS
"""
from TTS.api import TTS
import sys


def clone_voice(reference_audio: str, text: str, output_path: str = "cloned_voice.wav"):
    """
    Clone voice from reference audio and synthesize text.
    reference_audio: 5-10 second WAV of the target voice
    """
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=False)
    tts.tts_to_file(
        text=text,
        speaker_wav=reference_audio,
        language="en",
        file_path=output_path
    )
    print(f"Cloned voice saved: {output_path}")
    print("Play this through Virtual Audio Cable to demo voice deepfake attack.")


if __name__ == "__main__":
    ref = sys.argv[1] if len(sys.argv) > 1 else "reference.wav"
    text = "Please authorize this transaction of ten lakh rupees immediately."
    clone_voice(ref, text)
