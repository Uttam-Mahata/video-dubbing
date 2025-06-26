from functools import lru_cache
from src.services import GeminiService, FileService, VideoDubbingService
from src.repositories import (
    FileVideoFileRepository, 
    FileDubbingRequestRepository, 
    FileDubbingResultRepository
)
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@lru_cache()
def get_settings():
    """Get application settings"""
    return {
        "gemini_api_key": os.getenv("GEMINI_API_KEY"),
        "upload_dir": os.getenv("UPLOAD_DIR", "uploads"),
        "output_dir": os.getenv("OUTPUT_DIR", "outputs"),
        "data_dir": os.getenv("DATA_DIR", "data")
    }


@lru_cache()
def get_gemini_service():
    """Get Gemini service instance"""
    settings = get_settings()
    if not settings["gemini_api_key"]:
        raise ValueError("GEMINI_API_KEY environment variable is required")
    return GeminiService(api_key=settings["gemini_api_key"])


@lru_cache()
def get_file_service():
    """Get file service instance"""
    settings = get_settings()
    return FileService(
        upload_dir=settings["upload_dir"],
        output_dir=settings["output_dir"]
    )


@lru_cache()
def get_video_file_repository():
    """Get video file repository instance"""
    settings = get_settings()
    return FileVideoFileRepository(storage_path=f"{settings['data_dir']}/videos")


@lru_cache()
def get_dubbing_request_repository():
    """Get dubbing request repository instance"""
    settings = get_settings()
    return FileDubbingRequestRepository(storage_path=f"{settings['data_dir']}/requests")


@lru_cache()
def get_dubbing_result_repository():
    """Get dubbing result repository instance"""
    settings = get_settings()
    return FileDubbingResultRepository(storage_path=f"{settings['data_dir']}/results")


def get_video_dubbing_service():
    """Get video dubbing service instance"""
    return VideoDubbingService(
        gemini_service=get_gemini_service(),
        file_service=get_file_service(),
        video_repo=get_video_file_repository(),
        request_repo=get_dubbing_request_repository(),
        result_repo=get_dubbing_result_repository()
    )
