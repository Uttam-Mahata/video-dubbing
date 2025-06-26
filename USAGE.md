# 🎬 Gemini Video Dubbing API - Usage Guide

## Quick Start Commands

### 1. Setup the Application
```bash
# Clone and setup
git clone <repository>
cd video-dubbing
chmod +x setup.sh
./setup.sh

# Edit environment file
nano .env  # Add your GEMINI_API_KEY
```

### 2. Run the Application
```bash
# Activate virtual environment
source venv/bin/activate

# Start the server
python app.py
```

### 3. Test the API
```bash
# Check if server is running
curl http://localhost:8000/health

# List available voices
curl http://localhost:8000/api/v1/dubbing/voices
```

### 4. Upload and Process Video
```bash
# Upload a video file
curl -X POST "http://localhost:8000/api/v1/dubbing/upload" \
  -F "file=@sample_video.mp4" \
  -F "target_language=en-US" \
  -F "voice_style=natural"

# Response will include request_id like:
# {"request_id": "abc123", "status": "pending", "message": "..."}
```

### 5. Check Processing Status
```bash
# Check status (replace abc123 with your request_id)
curl "http://localhost:8000/api/v1/dubbing/status/abc123"
```

### 6. Download Result
```bash
# Download dubbed audio when completed
curl "http://localhost:8000/api/v1/dubbing/download/abc123" -o dubbed_audio.wav
```

## Python Client Example

```python
from client_example import VideoDubbingClient

# Initialize client
client = VideoDubbingClient("http://localhost:8000")

# Simple usage
result = client.upload_video("video.mp4")
status = client.wait_for_completion(result['request_id'])
client.download_audio(result['request_id'], "output.wav")
```

## API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Web interface |
| GET | `/health` | Health check |
| GET | `/docs` | Swagger documentation |
| POST | `/api/v1/dubbing/upload` | Upload video for dubbing |
| GET | `/api/v1/dubbing/status/{id}` | Check processing status |
| GET | `/api/v1/dubbing/download/{id}` | Download dubbed audio |
| POST | `/api/v1/dubbing/custom` | Custom voice configuration |
| GET | `/api/v1/dubbing/voices` | List available voices |

## Voice Selection Guide

### Character Types
- **Authoritative**: Kore, Orus, Alnilam
- **Friendly**: Achird, Callirrhoe, Vindemiatrix  
- **Energetic**: Puck, Fenrir, Sadachbia
- **Calm**: Algieba, Despina, Achernar
- **Professional**: Charon, Rasalgethi, Iapetus

### Example Custom Configuration
```json
{
  "video_id": "abc123",
  "speaker_configurations": [
    {
      "speaker_name": "Narrator",
      "voice_name": "Kore",
      "voice_style": "authoritative"
    },
    {
      "speaker_name": "Character",
      "voice_name": "Puck", 
      "voice_style": "energetic"
    }
  ],
  "target_language": "en-US"
}
```

## File Requirements

### Supported Formats
- MP4, AVI, MOV, WebM
- MPEG, FLV, MPG, WMV, 3GPP

### Size Limits
- Maximum file size: 100MB
- Maximum duration: 2 hours
- Recommended: Under 50MB for faster processing

### Quality Tips
- Use clear audio (minimal background noise)
- Ensure speakers are distinct
- Good video resolution helps with analysis

## Troubleshooting

### Common Issues

1. **"GEMINI_API_KEY not found"**
   ```bash
   # Check environment file
   cat .env | grep GEMINI_API_KEY
   ```

2. **Processing stuck**
   ```bash
   # Check server logs
   tail -f app.log
   ```

3. **File upload fails**
   ```bash
   # Check file format and size
   file video.mp4
   ls -lh video.mp4
   ```

### Debug Mode
```bash
# Run with debug logging
export LOG_LEVEL=DEBUG
python app.py
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| GEMINI_API_KEY | Yes | - | Google Gemini API key |
| UPLOAD_DIR | No | uploads | Upload directory |
| OUTPUT_DIR | No | outputs | Output directory |
| MAX_FILE_SIZE | No | 100MB | Maximum file size |
| DEFAULT_LANGUAGE | No | en-US | Default language |

## Performance Tips

### For Best Results
- Use videos with clear audio
- Separate speakers by at least 2 seconds
- Minimize background noise
- Use supported video formats

### Processing Time
- Simple videos (1 speaker, <1 min): ~30-60 seconds
- Complex videos (2 speakers, >5 min): ~2-5 minutes
- Large files (>50MB): Additional 1-2 minutes

## Production Deployment

### Docker
```dockerfile
FROM python:3.9
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Setup
```bash
# Production environment
export DEBUG=False
export LOG_LEVEL=WARNING
export MAX_FILE_SIZE=52428800  # 50MB for production
```

## Support

- 📖 API Documentation: http://localhost:8000/docs
- 🔧 GitHub Issues: [Create an issue]
- 📧 Email: support@alphaai.com

---

**Happy dubbing!** 🎭
