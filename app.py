from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from faster_whisper import WhisperModel
import time
import tempfile
import os

app = FastAPI(title="Audio Transcription API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Whisper model
model = WhisperModel("base", device="cuda", compute_type="int8")

def format_time(seconds):
    """Convert seconds to SRT time format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millisecs = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"

def group_words(words, min_words=4, max_words=6):
    """Group words into chunks of 4-6 words with their timing info"""
    groups = []
    
    i = 0
    while i < len(words):
        remaining_words = len(words) - i
        
        if remaining_words <= max_words:
            group = words[i:]
            groups.append(group)
            break
        elif remaining_words < min_words + max_words:
            group_size = remaining_words // 2 + (remaining_words % 2)
            group = words[i:i+group_size]
            groups.append(group)
            i += group_size
        else:
            group = words[i:i+max_words]
            groups.append(group)
            i += max_words
    
    return groups

def generate_srt(segments):
    """Convert segments to SRT format with 4-6 words per line"""
    srt_content = []
    subtitle_number = 1
    
    for segment in segments:
        if not hasattr(segment, 'words') or not segment.words:
            srt_content.extend([
                str(subtitle_number),
                f"{format_time(segment.start)} --> {format_time(segment.end)}",
                f"{segment.text.strip()}\n"
            ])
            subtitle_number += 1
            continue
        
        word_groups = group_words(segment.words)
        
        for group in word_groups:
            if not group:
                continue
            
            start_time = format_time(group[0].start)
            end_time = format_time(group[-1].end)
            text = ''.join(word.word for word in group).strip()
            
            srt_content.extend([
                str(subtitle_number),
                f"{start_time} --> {end_time}",
                f"{text}\n"
            ])
            
            subtitle_number += 1
    
    return "\n".join(srt_content)

@app.post("/transcribe/")
async def transcribe_audio(file: UploadFile = File(...)):
    start_time = time.time()
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_path = temp_file.name
    
    try:
        # Transcribe audio
        segments, info = model.transcribe(temp_path, beam_size=5, word_timestamps=True)
        
        # Generate SRT content
        srt_content = generate_srt(segments)
        
        duration = time.time() - start_time
        
        return {
            "status": "success",
            "language": info.language,
            "language_probability": info.language_probability,
            "processing_time": duration,
            "srt_content": srt_content
        }
    finally:
        # Clean up temporary file
        os.unlink(temp_path)

@app.get("/")
async def root():
    return {
        "message": "Audio Transcription API",
        "status": "running",
        "endpoints": {
            "transcribe": "/transcribe/"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8080, reload=True) 