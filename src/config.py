"""
Configuration management for the Video Dubbing Application
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    gemini_api_key: str = Field(..., env="GEMINI_API_KEY")
    host: str = Field("0.0.0.0", env="HOST")
    port: int = Field(8000, env="PORT")
    debug: bool = Field(True, env="DEBUG")
    
    # File Storage
    upload_dir: str = Field("uploads", env="UPLOAD_DIR")
    output_dir: str = Field("outputs", env="OUTPUT_DIR")
    data_dir: str = Field("data", env="DATA_DIR")
    
    # File Limits
    max_file_size: int = Field(104857600, env="MAX_FILE_SIZE")  # 100MB
    max_video_duration: int = Field(7200, env="MAX_VIDEO_DURATION")  # 2 hours
    
    # Processing Defaults
    default_language: str = Field("en-US", env="DEFAULT_LANGUAGE")
    default_voice_style: str = Field("natural", env="DEFAULT_VOICE_STYLE")
    
    # Gemini Models
    gemini_model: str = Field("gemini-2.0-flash", env="GEMINI_MODEL")
    gemini_tts_model: str = Field("gemini-2.5-flash-preview-tts", env="GEMINI_TTS_MODEL")
    
    # Logging
    log_level: str = Field("INFO", env="LOG_LEVEL")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
