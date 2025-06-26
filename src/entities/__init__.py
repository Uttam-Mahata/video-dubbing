from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
import uuid
from datetime import datetime


class SpeakerType(str, Enum):
    SINGLE = "single"
    MULTIPLE = "multiple"


class VoiceName(str, Enum):
    ZEPHYR = "Zephyr"
    PUCK = "Puck"
    CHARON = "Charon"
    KORE = "Kore"
    FENRIR = "Fenrir"
    LEDA = "Leda"
    ORUS = "Orus"
    AOEDE = "Aoede"
    CALLIRRHOE = "Callirrhoe"
    AUTONOE = "Autonoe"
    ENCELADUS = "Enceladus"
    IAPETUS = "Iapetus"
    UMBRIEL = "Umbriel"
    ALGIEBA = "Algieba"
    DESPINA = "Despina"
    ERINOME = "Erinome"
    ALGENIB = "Algenib"
    RASALGETHI = "Rasalgethi"
    LAOMEDEIA = "Laomedeia"
    ACHERNAR = "Achernar"
    ALNILAM = "Alnilam"
    SCHEDAR = "Schedar"
    GACRUX = "Gacrux"
    PULCHERRIMA = "Pulcherrima"
    ACHIRD = "Achird"
    ZUBENELGENUBI = "Zubenelgenubi"
    VINDEMIATRIX = "Vindemiatrix"
    SADACHBIA = "Sadachbia"
    SADALTAGER = "Sadaltager"
    SULAFAT = "Sulafat"


class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Speaker(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    voice_name: VoiceName
    dialogue_segments: List[str] = Field(default_factory=list)
    timestamps: List[tuple[float, float]] = Field(default_factory=list)  # (start, end) times


class VideoAnalysis(BaseModel):
    duration: float = Field(..., description="Video duration in seconds")
    speaker_count: int = Field(..., description="Number of speakers detected")
    speakers: List[Speaker] = Field(default_factory=list)
    transcript: str = Field(..., description="Full transcript of the video")
    dialogue_format: Optional[str] = Field(None, description="Formatted dialogue if multiple speakers")
    language_detected: Optional[str] = Field(None, description="Detected language code")
    
    
class VideoFile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str
    file_path: str
    file_size: int
    mime_type: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    gemini_file_uri: Optional[str] = Field(None, description="Gemini Files API URI")


class DubbingRequest(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    video_file: VideoFile
    target_language: Optional[str] = Field("en-US", description="Target language for dubbing")
    voice_style: Optional[str] = Field("natural", description="Voice style instructions")
    preserve_emotions: bool = Field(True, description="Whether to preserve emotional tone")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DubbingResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    request_id: str
    status: ProcessingStatus
    video_analysis: Optional[VideoAnalysis] = None
    audio_file_path: Optional[str] = None
    processing_time: Optional[float] = None
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


# Request/Response DTOs
class VideoUploadRequest(BaseModel):
    target_language: Optional[str] = Field("en-US")
    voice_style: Optional[str] = Field("natural")
    preserve_emotions: bool = Field(True)


class VideoAnalysisResponse(BaseModel):
    video_id: str
    duration: float
    speaker_count: int
    speakers: List[Dict[str, Any]]
    transcript: str
    dialogue_format: Optional[str] = None
    language_detected: Optional[str] = None


class DubbingRequestResponse(BaseModel):
    request_id: str
    status: ProcessingStatus
    message: str


class DubbingStatusResponse(BaseModel):
    request_id: str
    status: ProcessingStatus
    progress: Optional[float] = None
    video_analysis: Optional[VideoAnalysisResponse] = None
    audio_file_url: Optional[str] = None
    error_message: Optional[str] = None
    processing_time: Optional[float] = None


class SpeakerConfiguration(BaseModel):
    speaker_name: str
    voice_name: VoiceName
    voice_style: Optional[str] = Field("natural")


class CustomDubbingRequest(BaseModel):
    video_id: str
    speaker_configurations: List[SpeakerConfiguration]
    target_language: Optional[str] = Field("en-US")
    global_voice_style: Optional[str] = Field("natural")
