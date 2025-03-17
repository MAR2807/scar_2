from elevenlabs import ElevenLabs, VoiceSettings
import elevenlabs
import os
from tempfile import NamedTemporaryFile
import requests
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize ElevenLabs client for text-to-speech
client = ElevenLabs(
    api_key=os.getenv('ELEVENLABS_API_KEY')
)

# Initialize OpenAI client for speech-to-text
openai_client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY')
)

def text_to_speech(text):
    """Convert text to speech using ElevenLabs"""
    try:
        audio_generator = client.text_to_speech.convert(
            model_id="eleven_turbo_v2_5",
            voice_id="oWAxZDx7w5VEj9dCyTzz",  # Grace voice
            optimize_streaming_latency=0,
            output_format="mp3_22050_32",
            text=text,
            voice_settings=VoiceSettings(
                stability=0.5,
                similarity_boost=0.3,
                style=0.2,
            ),
        )
        elevenlabs.play(audio_generator)
        return True
    except Exception as e:
        print(f"Error in text_to_speech: {str(e)}")
        return False

def speech_to_text(audio_file):
    """Convert speech to text using OpenAI Whisper API"""
    try:
        with open(audio_file, 'rb') as audio:
            transcript = openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=audio,
                response_format="text"
            )
            return transcript
    except Exception as e:
        print(f"Error in speech_to_text: {str(e)}")
        return None

def save_audio_file(audio_data):
    """Save audio data to a temporary file"""
    try:
        # Create a temporary file
        with NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            temp_file.write(audio_data)
            return temp_file.name
    except Exception as e:
        print(f"Error saving audio file: {str(e)}")
        return None 