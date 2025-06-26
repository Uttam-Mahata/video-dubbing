from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from src.entities import VideoFile, DubbingRequest, DubbingResult, VideoAnalysis
import json
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class VideoFileRepository(ABC):
    """Abstract repository for video file operations"""
    
    @abstractmethod
    async def save(self, video_file: VideoFile) -> VideoFile:
        pass
    
    @abstractmethod
    async def get_by_id(self, file_id: str) -> Optional[VideoFile]:
        pass
    
    @abstractmethod
    async def delete(self, file_id: str) -> bool:
        pass
    
    @abstractmethod
    async def get_all(self) -> List[VideoFile]:
        pass


class DubbingRequestRepository(ABC):
    """Abstract repository for dubbing request operations"""
    
    @abstractmethod
    async def save(self, request: DubbingRequest) -> DubbingRequest:
        pass
    
    @abstractmethod
    async def get_by_id(self, request_id: str) -> Optional[DubbingRequest]:
        pass
    
    @abstractmethod
    async def get_all(self) -> List[DubbingRequest]:
        pass


class DubbingResultRepository(ABC):
    """Abstract repository for dubbing result operations"""
    
    @abstractmethod
    async def save(self, result: DubbingResult) -> DubbingResult:
        pass
    
    @abstractmethod
    async def get_by_id(self, result_id: str) -> Optional[DubbingResult]:
        pass
    
    @abstractmethod
    async def get_by_request_id(self, request_id: str) -> Optional[DubbingResult]:
        pass
    
    @abstractmethod
    async def update_status(self, result_id: str, status: str, **kwargs) -> bool:
        pass
    
    @abstractmethod
    async def get_all(self) -> List[DubbingResult]:
        pass


# File-based implementations (for development/demo)
class FileVideoFileRepository(VideoFileRepository):
    """File-based implementation for video file storage"""
    
    def __init__(self, storage_path: str = "data/videos"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.storage_path / "metadata.json"
        self._ensure_metadata_file()
    
    def _ensure_metadata_file(self):
        if not self.metadata_file.exists():
            with open(self.metadata_file, 'w') as f:
                json.dump({}, f)
    
    def _load_metadata(self) -> Dict[str, Any]:
        try:
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_metadata(self, metadata: Dict[str, Any]):
        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
    
    async def save(self, video_file: VideoFile) -> VideoFile:
        metadata = self._load_metadata()
        metadata[video_file.id] = video_file.model_dump()
        self._save_metadata(metadata)
        logger.info(f"Saved video file metadata: {video_file.id}")
        return video_file
    
    async def get_by_id(self, file_id: str) -> Optional[VideoFile]:
        metadata = self._load_metadata()
        if file_id in metadata:
            return VideoFile(**metadata[file_id])
        return None
    
    async def delete(self, file_id: str) -> bool:
        metadata = self._load_metadata()
        if file_id in metadata:
            video_file = VideoFile(**metadata[file_id])
            # Delete physical file
            if os.path.exists(video_file.file_path):
                os.remove(video_file.file_path)
            # Remove from metadata
            del metadata[file_id]
            self._save_metadata(metadata)
            logger.info(f"Deleted video file: {file_id}")
            return True
        return False
    
    async def get_all(self) -> List[VideoFile]:
        metadata = self._load_metadata()
        return [VideoFile(**data) for data in metadata.values()]


class FileDubbingRequestRepository(DubbingRequestRepository):
    """File-based implementation for dubbing request storage"""
    
    def __init__(self, storage_path: str = "data/requests"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.storage_path / "requests.json"
        self._ensure_metadata_file()
    
    def _ensure_metadata_file(self):
        if not self.metadata_file.exists():
            with open(self.metadata_file, 'w') as f:
                json.dump({}, f)
    
    def _load_metadata(self) -> Dict[str, Any]:
        try:
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_metadata(self, metadata: Dict[str, Any]):
        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
    
    async def save(self, request: DubbingRequest) -> DubbingRequest:
        metadata = self._load_metadata()
        metadata[request.id] = request.model_dump()
        self._save_metadata(metadata)
        logger.info(f"Saved dubbing request: {request.id}")
        return request
    
    async def get_by_id(self, request_id: str) -> Optional[DubbingRequest]:
        metadata = self._load_metadata()
        if request_id in metadata:
            return DubbingRequest(**metadata[request_id])
        return None
    
    async def get_all(self) -> List[DubbingRequest]:
        metadata = self._load_metadata()
        return [DubbingRequest(**data) for data in metadata.values()]


class FileDubbingResultRepository(DubbingResultRepository):
    """File-based implementation for dubbing result storage"""
    
    def __init__(self, storage_path: str = "data/results"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.storage_path / "results.json"
        self._ensure_metadata_file()
    
    def _ensure_metadata_file(self):
        if not self.metadata_file.exists():
            with open(self.metadata_file, 'w') as f:
                json.dump({}, f)
    
    def _load_metadata(self) -> Dict[str, Any]:
        try:
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_metadata(self, metadata: Dict[str, Any]):
        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
    
    async def save(self, result: DubbingResult) -> DubbingResult:
        metadata = self._load_metadata()
        metadata[result.id] = result.model_dump()
        self._save_metadata(metadata)
        logger.info(f"Saved dubbing result: {result.id}")
        return result
    
    async def get_by_id(self, result_id: str) -> Optional[DubbingResult]:
        metadata = self._load_metadata()
        if result_id in metadata:
            return DubbingResult(**metadata[result_id])
        return None
    
    async def get_by_request_id(self, request_id: str) -> Optional[DubbingResult]:
        metadata = self._load_metadata()
        for result_data in metadata.values():
            if result_data.get('request_id') == request_id:
                return DubbingResult(**result_data)
        return None
    
    async def update_status(self, result_id: str, status: str, **kwargs) -> bool:
        metadata = self._load_metadata()
        if result_id in metadata:
            metadata[result_id]['status'] = status
            for key, value in kwargs.items():
                metadata[result_id][key] = value
            self._save_metadata(metadata)
            logger.info(f"Updated result status: {result_id} -> {status}")
            return True
        return False
    
    async def get_all(self) -> List[DubbingResult]:
        metadata = self._load_metadata()
        return [DubbingResult(**data) for data in metadata.values()]
