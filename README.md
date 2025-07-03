# Audio Transcription with SRT Generation

This project provides a simple GUI application and API for transcribing audio files and generating SRT subtitles using the Faster Whisper model.

## Features

- Audio file transcription with word-level timestamps
- Automatic language detection
- SRT subtitle generation with 4-6 words per line
- Simple GUI interface for file selection and transcription
- REST API endpoint for programmatic access

## Requirements

- Python 3.8 or higher
- CUDA-capable GPU (for optimal performance)
- FFmpeg (for audio file processing)

## Installation

1. Clone this repository
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Starting the API Server

1. Run the API server:
   ```bash
   python app.py
   ```
   The server will start at `http://localhost:8080`

### Using the GUI Client

1. Run the GUI client:
   ```bash
   python client.py
   ```

2. Use the GUI to:
   - Select an audio file
   - Start transcription
   - View the generated SRT content
   - Save the SRT file

### API Endpoints

- `GET /`: Check API status
- `POST /transcribe/`: Upload and transcribe an audio file
  - Returns JSON with:
    - SRT content
    - Detected language
    - Language probability
    - Processing time

## Notes

- The transcription process uses the "base" Whisper model by default
- Processing time depends on the audio file length and your GPU capabilities
- Supported audio formats: WAV, MP3, FLAC, OGG, M4A 