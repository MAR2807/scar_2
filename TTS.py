
from elevenlabs import ElevenLabs, VoiceSettings
import elevenlabs



def text_to_speech():
        
        
        #USE GRACE(LEGACY) VOICE#
        #voice ID: oWAxZDx7w5VEj9dCyTzz

        client = ElevenLabs(
            api_key="sk_dce04ff3e0541155c2e8cd48bb13478184f276599b45607a",
        )
        audio_generator = client.text_to_speech.convert(
            model_id="eleven_turbo_v2_5",
            voice_id="oWAxZDx7w5VEj9dCyTzz",
            optimize_streaming_latency=0,
            output_format="mp3_22050_32",
            text='"Hi! This is scarlett from khan marketing group. You clicked on one of our ads about marketing. What services were you interested in?',
            voice_settings=VoiceSettings(
                stability=0.5,
                similarity_boost=0.3,
                style=0.2,
            ),
        )
        elevenlabs.play(audio_generator)
if __name__ == "__main__":
    text_to_speech()