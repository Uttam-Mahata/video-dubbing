from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import logging
import os
from pathlib import Path

# Import routers
from src.routers import router as dubbing_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Gemini Video Dubbing API",
    description="""
    A powerful Video Dubbing Application powered by Google Gemini AI.
    
    ## Features
    
    * **Video Analysis**: Automatically analyze videos to detect speakers, duration, and generate transcripts
    * **Smart Voice Mapping**: AI-powered voice selection based on speaker characteristics
    * **Multi-Speaker Support**: Handle conversations with multiple speakers
    * **Custom Voice Configuration**: Manually assign voices to specific speakers
    * **Emotion Preservation**: Maintain emotional tone and style from original content
    * **Multiple Languages**: Support for 24+ languages
    * **Structured Output**: JSON-formatted analysis results
    
    ## Supported Video Formats
    
    * MP4, AVI, MOV, WebM, MPEG, FLV, MPG, WMV, 3GPP
    
    ## Available Voice Options
    
    30+ unique voices with different characteristics:
    - Bright, Upbeat, Informative, Firm, Excitable
    - Youthful, Breezy, Easy-going, Breathy, Clear
    - Smooth, Gravelly, Soft, Even, Mature
    - Forward, Friendly, Casual, Gentle, Lively
    - Knowledgeable, Warm
    
    ## Workflow
    
    1. **Upload Video**: POST `/api/v1/dubbing/upload`
    2. **Check Status**: GET `/api/v1/dubbing/status/{request_id}`
    3. **Download Result**: GET `/api/v1/dubbing/download/{request_id}`
    4. **Custom Configuration**: POST `/api/v1/dubbing/custom` (optional)
    """,
    version="1.0.0",
    contact={
        "name": "Alpha AI Service Pvt Ltd",
        "email": "support@alphaai.com",
    },
    license_info={
        "name": "MIT License",
    },
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(dubbing_router)

# Create necessary directories
for directory in ["uploads", "outputs", "data/videos", "data/requests", "data/results"]:
    Path(directory).mkdir(parents=True, exist_ok=True)

# Mount static files for serving audio files
if not os.path.exists("outputs"):
    os.makedirs("outputs")
app.mount("/static", StaticFiles(directory="outputs"), name="static")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with API documentation"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Gemini Video Dubbing API</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #1976d2; }
            h2 { color: #424242; }
            .feature { background: #e3f2fd; padding: 15px; margin: 10px 0; border-radius: 5px; }
            .code { background: #f5f5f5; padding: 10px; border-radius: 5px; font-family: monospace; }
            a { color: #1976d2; text-decoration: none; }
            a:hover { text-decoration: underline; }
            .btn { background: #1976d2; color: white; padding: 10px 20px; border-radius: 5px; display: inline-block; margin: 10px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎬 Gemini Video Dubbing API</h1>
            <p>Welcome to the most advanced AI-powered video dubbing service!</p>
            
            <h2>🚀 Quick Start</h2>
            <div class="feature">
                <h3>1. Upload a Video</h3>
                <div class="code">
                    curl -X POST "http://localhost:8000/api/v1/dubbing/upload" \\<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;-F "file=@your_video.mp4" \\<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;-F "target_language=en-US" \\<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;-F "voice_style=natural"
                </div>
            </div>
            
            <div class="feature">
                <h3>2. Check Processing Status</h3>
                <div class="code">
                    curl "http://localhost:8000/api/v1/dubbing/status/{request_id}"
                </div>
            </div>
            
            <div class="feature">
                <h3>3. Download Dubbed Audio</h3>
                <div class="code">
                    curl "http://localhost:8000/api/v1/dubbing/download/{request_id}" -o dubbed_audio.wav
                </div>
            </div>
            
            <h2>📊 Features</h2>
            <div class="feature">
                <strong>🎯 Smart Analysis:</strong> Automatically detects speakers, emotions, and generates accurate transcripts
            </div>
            <div class="feature">
                <strong>🎭 Voice Variety:</strong> 30+ unique voices with different characteristics and emotions
            </div>
            <div class="feature">
                <strong>🌍 Multi-Language:</strong> Support for 24+ languages including English, Spanish, French, German, and more
            </div>
            <div class="feature">
                <strong>⚙️ Customizable:</strong> Configure specific voices for each speaker
            </div>
            <div class="feature">
                <strong>🎪 Emotion Preservation:</strong> Maintains the emotional tone and style of original content
            </div>
            
            <h2>🛠️ API Documentation</h2>
            <a href="/docs" class="btn">📖 Interactive API Docs (Swagger)</a>
            <a href="/redoc" class="btn">📋 Alternative Docs (ReDoc)</a>
            
            <h2>🎨 Available Voices</h2>
            <a href="/api/v1/dubbing/voices" class="btn">🎤 View All Voices</a>
            
            <h2>💡 Example Use Cases</h2>
            <ul>
                <li><strong>Content Localization:</strong> Dub videos for different markets</li>
                <li><strong>Accessibility:</strong> Create audio versions of video content</li>
                <li><strong>Education:</strong> Generate multilingual educational content</li>
                <li><strong>Entertainment:</strong> Create voiceovers for animation or films</li>
                <li><strong>Corporate:</strong> Localize training and presentation videos</li>
            </ul>
            
            <hr>
            <p><em>Powered by Google Gemini AI • Built with FastAPI • Created by Alpha AI Service Pvt Ltd</em></p>
        </div>
    </body>
    </html>
    """


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "gemini-video-dubbing-api",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    
    # Check for required environment variable
    if not os.getenv("GEMINI_API_KEY"):
        logger.error("GEMINI_API_KEY environment variable is required!")
        exit(1)
    
    logger.info("Starting Gemini Video Dubbing API...")
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )