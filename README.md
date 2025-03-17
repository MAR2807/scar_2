# Voice Assistant Web Application

A web-based voice assistant application that combines OpenAI's Whisper for speech-to-text and ElevenLabs for text-to-speech capabilities. Users can record their voice through the browser, get accurate transcriptions, and receive voice responses.

## Features

- Real-time audio recording with visual waveform display
- Speech-to-text transcription using OpenAI's Whisper API
- Text-to-speech response using ElevenLabs' API
- Modern, responsive web interface
- Visual feedback during recording
- Error handling and status messages

## Prerequisites

- Python 3.8 or higher
- OpenAI API key
- ElevenLabs API key

## Installation

1. Clone the repository:
```bash
git clone <your-repository-url>
cd <repository-name>
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory and add your API keys:
```
OPENAI_API_KEY=your_openai_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
```

## Usage

1. Start the Flask application:
```bash
python app.py
```

2. Open your web browser and navigate to `http://localhost:5000`

3. Click the "Start Recording" button and allow microphone access

4. Speak into your microphone

5. Click "Stop Recording" when finished

6. The application will transcribe your speech and respond with a voice message

## Project Structure

- `app.py` - Main Flask application
- `speech_recognition.py` - Speech-to-text and text-to-speech functionality
- `templates/upload.html` - Web interface template
- `requirements.txt` - Project dependencies
- `.env` - Environment variables (not included in repository)

## Security Notes

- Never commit your API keys to the repository
- Use environment variables for sensitive information
- This is a development server - use a production WSGI server for deployment

## License

MIT License - feel free to use this project for your own purposes.

## Contributing

Feel free to submit issues and pull requests.
