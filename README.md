# 🎬 Gemini Video Dubbing API

A powerful, AI-driven video dubbing application built with Google Gemini and FastAPI. This application analyzes videos, detects speakers, generates transcripts, and creates high-quality dubbed audio with customizable voices and emotional preservation.

## ✨ Features

### 🎯 Core Capabilities
- **Smart Video Analysis**: Automatically detect speakers, duration, and emotional tone
- **Multi-Speaker Support**: Handle conversations with up to 2 distinct speakers
- **30+ Voice Options**: Wide variety of voices with different characteristics
- **24+ Languages**: Support for major world languages
- **Emotion Preservation**: Maintain original emotional tone and style
- **Custom Voice Mapping**: Manually assign specific voices to speakers
- **Structured Output**: JSON-formatted analysis results

### 🔧 Technical Features
- **4-Layer Architecture**: Clean separation of concerns (Entity, Repository, Service, Router)
- **Async Processing**: Non-blocking video processing
- **File Management**: Secure file upload and storage
- **REST API**: Comprehensive RESTful endpoints
- **Interactive Documentation**: Auto-generated Swagger/OpenAPI docs
- **Error Handling**: Robust error handling and validation

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Google Gemini API Key
- 100MB+ available disk space

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/your-repo/video-dubbing.git
cd video-dubbing
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment**
```bash
cp .env.example .env
# Edit .env with your Gemini API key
```

4. **Run the application**
```bash
python app.py
```

The API will be available at `http://localhost:8000`

## 📖 API Documentation

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Main Endpoints

#### 1. Upload Video for Dubbing
```http
POST /api/v1/dubbing/upload
```

**Parameters:**
- `file`: Video file (MP4, AVI, MOV, WebM, etc.)
- `target_language`: Target language (default: "en-US")
- `voice_style`: Voice style (default: "natural")
- `preserve_emotions`: Preserve emotional tone (default: true)

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/dubbing/upload" \
  -F "file=@video.mp4" \
  -F "target_language=en-US" \
  -F "voice_style=natural"
```

#### 2. Check Processing Status
```http
GET /api/v1/dubbing/status/{request_id}
```

**Example:**
```bash
curl "http://localhost:8000/api/v1/dubbing/status/12345"
```

#### 3. Download Dubbed Audio
```http
GET /api/v1/dubbing/download/{request_id}
```

**Example:**
```bash
curl "http://localhost:8000/api/v1/dubbing/download/12345" -o dubbed_audio.wav
```

#### 4. Custom Voice Configuration
```http
POST /api/v1/dubbing/custom
```

**Example:**
```json
{
  "video_id": "12345",
  "speaker_configurations": [
    {
      "speaker_name": "John",
      "voice_name": "Kore",
      "voice_style": "authoritative"
    },
    {
      "speaker_name": "Jane", 
      "voice_name": "Leda",
      "voice_style": "friendly"
    }
  ],
  "target_language": "en-US"
}
```

#### 5. List Available Voices
```http
GET /api/v1/dubbing/voices
```

## 🎤 Available Voices

The API supports 30+ unique voices with different characteristics:

| Voice | Characteristics | Best For |
|-------|----------------|----------|
| Zephyr | Bright | Cheerful content, upbeat dialogue |
| Puck | Upbeat | Energetic speakers, enthusiastic content |
| Kore | Firm | Authoritative speakers, business content |
| Leda | Youthful | Young speakers, casual conversation |
| Enceladus | Breathy | Soft dialogue, intimate content |
| Gacrux | Mature | Experienced voices, professional content |
| ... | ... | ... |

*View complete list at: `/api/v1/dubbing/voices`*

## 🌍 Supported Languages

- English (US, India)
- Spanish (US)
- French (France)
- German (Germany)
- Italian (Italy)
- Portuguese (Brazil)
- Japanese (Japan)
- Korean (Korea)
- Chinese (Mandarin)
- Hindi (India)
- Arabic (Egyptian)
- Russian (Russia)
- Dutch (Netherlands)
- Polish (Poland)
- Thai (Thailand)
- Turkish (Turkey)
- Vietnamese (Vietnam)
- Romanian (Romania)
- Ukrainian (Ukraine)
- Bengali (Bangladesh)
- Marathi (India)
- Tamil (India)
- Telugu (India)

## 📁 Project Structure

```
video-dubbing/
├── src/
│   ├── entities/           # Domain models and DTOs
│   ├── repositories/       # Data access layer
│   ├── services/          # Business logic layer
│   ├── routers/           # API endpoints
│   ├── config.py          # Configuration management
│   ├── dependencies.py    # Dependency injection
│   └── utils.py           # Utility functions
├── uploads/               # Uploaded video files
├── outputs/               # Generated audio files
├── data/                  # Application data storage
├── app.py                 # Main FastAPI application
├── client_example.py      # Example API client
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
└── README.md             # This file
```

## 🎯 Use Cases

### Content Localization
Transform videos for global audiences by dubbing in multiple languages while preserving speaker characteristics and emotional tone.

### Accessibility
Create audio versions of video content for visually impaired audiences or audio-only consumption.

### Education
Generate multilingual educational content, lectures, and training materials.

### Entertainment
Create voiceovers for animation, films, podcasts, and audiobooks.

### Corporate Training
Localize training videos and presentations for international teams.

## 🛠️ Development

### Running Tests
```bash
# Unit tests
python -m pytest tests/

# Integration tests
python -m pytest tests/integration/
```

### Development Server
```bash
# Run with auto-reload
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | Required |
| `UPLOAD_DIR` | Upload directory | "uploads" |
| `OUTPUT_DIR` | Output directory | "outputs" |
| `DATA_DIR` | Data storage directory | "data" |
| `MAX_FILE_SIZE` | Max file size (bytes) | 104857600 |
| `DEFAULT_LANGUAGE` | Default target language | "en-US" |

## 📊 Performance & Limits

### File Limits
- **Maximum file size**: 100MB (configurable)
- **Maximum duration**: 2 hours
- **Supported formats**: MP4, AVI, MOV, WebM, MPEG, FLV, MPG, WMV, 3GPP

### Processing Time
- **Simple videos** (1 speaker, < 1 min): ~30-60 seconds
- **Complex videos** (2 speakers, > 5 min): ~2-5 minutes
- **Processing is asynchronous** - check status endpoint for updates

### API Rate Limits
- **Free tier**: 8 hours of YouTube video per day
- **Paid tier**: No video length limits
- **Concurrent requests**: Handled via async processing

## 🔧 Configuration

### Voice Style Options
- `natural` - Default, balanced tone
- `dramatic` - Enhanced emotional expression  
- `cheerful` - Upbeat and positive
- `authoritative` - Confident and firm
- `gentle` - Soft and calm
- `energetic` - High energy and enthusiasm

### Language Codes
Use standard BCP-47 language codes:
- `en-US` - English (US)
- `es-US` - Spanish (US)
- `fr-FR` - French (France)
- `de-DE` - German (Germany)
- `ja-JP` - Japanese (Japan)
- ... (see full list in supported languages)

## 🤝 Example Usage with Python Client

```python
from client_example import VideoDubbingClient

# Initialize client
client = VideoDubbingClient("http://localhost:8000")

# Upload video
result = client.upload_video(
    "my_video.mp4",
    target_language="en-US",
    voice_style="natural"
)

# Wait for completion
final_status = client.wait_for_completion(result['request_id'])

# Download result
client.download_audio(result['request_id'], "dubbed_audio.wav")
```

## 🐛 Troubleshooting

### Common Issues

1. **"GEMINI_API_KEY not found"**
   - Ensure your `.env` file contains a valid Gemini API key
   - Verify the key has necessary permissions

2. **"File too large" error**
   - Check file size (default limit: 100MB)
   - Compress video or adjust `MAX_FILE_SIZE` in environment

3. **Processing stuck at "pending"**
   - Check logs for errors
   - Verify internet connection for Gemini API access
   - Ensure sufficient disk space

4. **Audio quality issues**
   - Try different voice configurations
   - Adjust voice style parameters
   - Check source video audio quality

### Debugging

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
python app.py
```

Check logs for detailed processing information.

## 📝 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- **Google Gemini AI** - For powerful multimodal AI capabilities
- **FastAPI** - For the excellent web framework
- **Pydantic** - For data validation and serialization

## 📞 Support

For issues and questions:
- 📧 Email: support@alphaai.com
- 📋 GitHub Issues: [Create an issue](https://github.com/your-repo/video-dubbing/issues)
- 📖 Documentation: [API Docs](http://localhost:8000/docs)

---

