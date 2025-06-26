"""
Utility functions for the Video Dubbing Application
"""
import mimetypes
from pathlib import Path
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


def get_supported_video_formats() -> List[str]:
    """Get list of supported video MIME types"""
    return [
        "video/mp4",
        "video/mpeg", 
        "video/mov",
        "video/avi",
        "video/x-flv",
        "video/mpg",
        "video/webm",
        "video/wmv",
        "video/3gpp"
    ]


def get_file_mime_type(file_path: str) -> str:
    """Get MIME type of a file"""
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type or "application/octet-stream"


def validate_video_file(file_path: str, max_size: int = 100 * 1024 * 1024) -> Tuple[bool, str]:
    """Validate video file"""
    path = Path(file_path)
    
    if not path.exists():
        return False, "File does not exist"
    
    # Check file size
    if path.stat().st_size > max_size:
        return False, f"File too large (max {max_size / 1024 / 1024:.0f}MB)"
    
    # Check MIME type
    mime_type = get_file_mime_type(file_path)
    if mime_type not in get_supported_video_formats():
        return False, f"Unsupported file type: {mime_type}"
    
    return True, "Valid video file"


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    # Remove or replace unsafe characters
    import re
    
    # Remove path separators and other unsafe characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Limit length
    if len(filename) > 255:
        name, ext = Path(filename).stem, Path(filename).suffix
        filename = name[:255-len(ext)] + ext
    
    return filename


def parse_timestamp(timestamp_str: str) -> float:
    """Parse timestamp string (MM:SS or HH:MM:SS) to seconds"""
    try:
        parts = timestamp_str.split(':')
        if len(parts) == 2:  # MM:SS
            minutes, seconds = map(float, parts)
            return minutes * 60 + seconds
        elif len(parts) == 3:  # HH:MM:SS
            hours, minutes, seconds = map(float, parts)
            return hours * 3600 + minutes * 60 + seconds
        else:
            raise ValueError("Invalid timestamp format")
    except (ValueError, TypeError) as e:
        logger.error(f"Failed to parse timestamp '{timestamp_str}': {e}")
        return 0.0


def format_timestamp(seconds: float) -> str:
    """Format seconds to timestamp string (MM:SS)"""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"


def estimate_processing_time(file_size: int, duration: float, speaker_count: int) -> float:
    """Estimate processing time based on file characteristics"""
    # Base processing time (seconds)
    base_time = 30
    
    # Size factor (larger files take longer)
    size_factor = file_size / (10 * 1024 * 1024)  # 10MB baseline
    
    # Duration factor
    duration_factor = duration / 60  # per minute
    
    # Speaker complexity factor
    speaker_factor = speaker_count * 1.5
    
    estimated_time = base_time + (size_factor * 10) + (duration_factor * 20) + (speaker_factor * 15)
    
    return max(30, min(estimated_time, 1800))  # Between 30 seconds and 30 minutes


class ProgressTracker:
    """Track processing progress"""
    
    def __init__(self):
        self.steps = [
            ("upload", "Uploading to Gemini"),
            ("analysis", "Analyzing video content"),
            ("transcription", "Generating transcript"),
            ("voice_mapping", "Mapping voices to speakers"),
            ("speech_generation", "Generating dubbed audio"),
            ("finalization", "Finalizing output")
        ]
        self.current_step = 0
    
    def get_progress(self) -> Dict:
        """Get current progress information"""
        if self.current_step >= len(self.steps):
            return {
                "progress": 1.0,
                "step": "completed",
                "description": "Processing completed"
            }
        
        step_name, description = self.steps[self.current_step]
        progress = self.current_step / len(self.steps)
        
        return {
            "progress": progress,
            "step": step_name,
            "description": description
        }
    
    def next_step(self):
        """Move to next processing step"""
        self.current_step += 1
    
    def complete(self):
        """Mark processing as complete"""
        self.current_step = len(self.steps)
