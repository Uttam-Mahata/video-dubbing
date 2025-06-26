from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from typing import List, Optional
import logging
from src.entities import (
    VideoUploadRequest, DubbingRequestResponse, DubbingStatusResponse,
    CustomDubbingRequest, SpeakerConfiguration, VoiceName, ProcessingStatus
)
from src.services import VideoDubbingService
from src.dependencies import get_video_dubbing_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/dubbing", tags=["Video Dubbing"])


@router.post("/upload", response_model=DubbingRequestResponse)
async def upload_video(
    file: UploadFile = File(...),
    target_language: Optional[str] = "en-US",
    voice_style: Optional[str] = "natural",
    preserve_emotions: bool = True,
    service: VideoDubbingService = Depends(get_video_dubbing_service)
):
    """
    Upload a video file for dubbing analysis and processing.
    
    - **file**: Video file to upload (MP4, AVI, MOV, WebM)
    - **target_language**: Target language for dubbing (default: en-US)
    - **voice_style**: Voice style for dubbing (natural, dramatic, cheerful, etc.)
    - **preserve_emotions**: Whether to preserve emotional tone from original
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Check file size (limit to 100MB for demo)
        file_content = await file.read()
        if len(file_content) > 100 * 1024 * 1024:  # 100MB
            raise HTTPException(status_code=413, detail="File too large (max 100MB)")
        
        # Validate file type
        allowed_types = [
            "video/mp4", "video/avi", "video/mov", "video/webm",
            "video/mpeg", "video/x-flv", "video/mpg", "video/wmv", "video/3gpp"
        ]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_types)}"
            )
        
        # Process the upload
        result = await service.process_video_upload(
            file_content=file_content,
            filename=file.filename,
            target_language=target_language,
            voice_style=voice_style,
            preserve_emotions=preserve_emotions
        )
        
        return DubbingRequestResponse(
            request_id=result.request_id,
            status=result.status,
            message="Video uploaded successfully. Processing started."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail="Upload failed")


@router.get("/status/{request_id}", response_model=DubbingStatusResponse)
async def get_dubbing_status(
    request_id: str,
    service: VideoDubbingService = Depends(get_video_dubbing_service)
):
    """
    Get the status of a dubbing request.
    
    - **request_id**: The ID of the dubbing request
    """
    try:
        result = await service.get_dubbing_status(request_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="Request not found")
        
        # Calculate progress based on status
        progress_map = {
            ProcessingStatus.PENDING: 0.0,
            ProcessingStatus.PROCESSING: 0.5,
            ProcessingStatus.COMPLETED: 1.0,
            ProcessingStatus.FAILED: 0.0
        }
        
        response = DubbingStatusResponse(
            request_id=request_id,
            status=result.status,
            progress=progress_map.get(result.status, 0.0),
            error_message=result.error_message,
            processing_time=result.processing_time
        )
        
        # Add video analysis if available
        if result.video_analysis:
            analysis = result.video_analysis
            # Handle both dict and VideoAnalysis object cases
            if isinstance(analysis, dict):
                response.video_analysis = {
                    "video_id": request_id,
                    "duration": analysis.get("duration", 0),
                    "speaker_count": analysis.get("speaker_count", 0),
                    "speakers": analysis.get("speakers", []),
                    "transcript": analysis.get("transcript", ""),
                    "dialogue_format": analysis.get("dialogue_format"),
                    "language_detected": analysis.get("language_detected")
                }
            else:
                # Assume it's a VideoAnalysis object
                response.video_analysis = {
                    "video_id": request_id,
                    "duration": getattr(analysis, "duration", 0),
                    "speaker_count": getattr(analysis, "speaker_count", 0),
                    "speakers": getattr(analysis, "speakers", []),
                    "transcript": getattr(analysis, "transcript", ""),
                    "dialogue_format": getattr(analysis, "dialogue_format", None),
                    "language_detected": getattr(analysis, "language_detected", None)
                }
        
        # Add audio file URL if completed
        if result.status == ProcessingStatus.COMPLETED and result.audio_file_path:
            response.audio_file_url = f"/api/v1/dubbing/download/{request_id}"
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail="Status check failed")


@router.get("/download/{request_id}")
async def download_dubbed_audio(
    request_id: str,
    service: VideoDubbingService = Depends(get_video_dubbing_service)
):
    """
    Download the dubbed audio file.
    
    - **request_id**: The ID of the dubbing request
    """
    try:
        result = await service.get_dubbing_status(request_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="Request not found")
        
        if result.status != ProcessingStatus.COMPLETED:
            raise HTTPException(status_code=400, detail="Dubbing not completed yet")
        
        if not result.audio_file_path:
            raise HTTPException(status_code=404, detail="Audio file not found")
        
        return FileResponse(
            path=result.audio_file_path,
            media_type="audio/wav",
            filename=f"dubbed_audio_{request_id}.wav"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Download failed: {e}")
        raise HTTPException(status_code=500, detail="Download failed")


@router.post("/custom", response_model=DubbingRequestResponse)
async def custom_dubbing(
    request: CustomDubbingRequest,
    service: VideoDubbingService = Depends(get_video_dubbing_service)
):
    """
    Create a custom dubbing with specific speaker configurations.
    
    - **video_id**: ID of the already uploaded video
    - **speaker_configurations**: Custom voice assignments for each speaker
    - **target_language**: Target language for dubbing
    - **global_voice_style**: Overall voice style to apply
    """
    try:
        result = await service.process_custom_dubbing(request)
        
        return DubbingRequestResponse(
            request_id=result.request_id,
            status=result.status,
            message="Custom dubbing started with specified configurations."
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Custom dubbing failed: {e}")
        raise HTTPException(status_code=500, detail="Custom dubbing failed")


@router.get("/voices", response_model=List[dict])
async def get_available_voices():
    """
    Get list of available voices for dubbing.
    """
    voices = []
    for voice in VoiceName:
        # Voice characteristics mapping
        characteristics = {
            VoiceName.ZEPHYR: "Bright",
            VoiceName.PUCK: "Upbeat",
            VoiceName.CHARON: "Informative",
            VoiceName.KORE: "Firm",
            VoiceName.FENRIR: "Excitable",
            VoiceName.LEDA: "Youthful",
            VoiceName.ORUS: "Firm",
            VoiceName.AOEDE: "Breezy",
            VoiceName.CALLIRRHOE: "Easy-going",
            VoiceName.AUTONOE: "Bright",
            VoiceName.ENCELADUS: "Breathy",
            VoiceName.IAPETUS: "Clear",
            VoiceName.UMBRIEL: "Easy-going",
            VoiceName.ALGIEBA: "Smooth",
            VoiceName.DESPINA: "Smooth",
            VoiceName.ERINOME: "Clear",
            VoiceName.ALGENIB: "Gravelly",
            VoiceName.RASALGETHI: "Informative",
            VoiceName.LAOMEDEIA: "Upbeat",
            VoiceName.ACHERNAR: "Soft",
            VoiceName.ALNILAM: "Firm",
            VoiceName.SCHEDAR: "Even",
            VoiceName.GACRUX: "Mature",
            VoiceName.PULCHERRIMA: "Forward",
            VoiceName.ACHIRD: "Friendly",
            VoiceName.ZUBENELGENUBI: "Casual",
            VoiceName.VINDEMIATRIX: "Gentle",
            VoiceName.SADACHBIA: "Lively",
            VoiceName.SADALTAGER: "Knowledgeable",
            VoiceName.SULAFAT: "Warm"
        }
        
        voices.append({
            "name": voice.value,
            "characteristics": characteristics.get(voice, "Natural"),
            "recommended_for": _get_voice_recommendations(voice)
        })
    
    return voices


def _get_voice_recommendations(voice: VoiceName) -> List[str]:
    """Get recommendations for when to use each voice"""
    recommendations = {
        VoiceName.ZEPHYR: ["cheerful content", "upbeat dialogue"],
        VoiceName.PUCK: ["energetic speakers", "enthusiastic content"],
        VoiceName.CHARON: ["educational content", "documentaries"],
        VoiceName.KORE: ["authoritative speakers", "business content"],
        VoiceName.FENRIR: ["excited dialogue", "dynamic content"],
        VoiceName.LEDA: ["young speakers", "casual conversation"],
        VoiceName.ORUS: ["strong male voices", "serious content"],
        VoiceName.AOEDE: ["relaxed dialogue", "casual content"],
        VoiceName.CALLIRRHOE: ["friendly conversation", "approachable content"],
        VoiceName.AUTONOE: ["clear dialogue", "professional content"],
        VoiceName.ENCELADUS: ["soft dialogue", "intimate content"],
        VoiceName.IAPETUS: ["clear narration", "instructional content"],
        VoiceName.UMBRIEL: ["casual dialogue", "relaxed content"],
        VoiceName.ALGIEBA: ["smooth narration", "professional content"],
        VoiceName.DESPINA: ["gentle dialogue", "calm content"],
        VoiceName.ERINOME: ["clear speech", "presentations"],
        VoiceName.ALGENIB: ["character voices", "distinctive speakers"],
        VoiceName.RASALGETHI: ["informative content", "explanations"],
        VoiceName.LAOMEDEIA: ["positive content", "uplifting dialogue"],
        VoiceName.ACHERNAR: ["gentle content", "soothing dialogue"],
        VoiceName.ALNILAM: ["confident speakers", "assertive content"],
        VoiceName.SCHEDAR: ["balanced dialogue", "neutral content"],
        VoiceName.GACRUX: ["mature speakers", "experienced voices"],
        VoiceName.PULCHERRIMA: ["direct dialogue", "straightforward content"],
        VoiceName.ACHIRD: ["warm dialogue", "welcoming content"],
        VoiceName.ZUBENELGENUBI: ["informal dialogue", "relaxed conversation"],
        VoiceName.VINDEMIATRIX: ["kind dialogue", "supportive content"],
        VoiceName.SADACHBIA: ["animated dialogue", "lively content"],
        VoiceName.SADALTAGER: ["expert content", "educational material"],
        VoiceName.SULAFAT: ["warm content", "comforting dialogue"]
    }
    
    return recommendations.get(voice, ["general purpose"])


@router.get("/requests", response_model=List[DubbingStatusResponse])
async def list_dubbing_requests(
    limit: Optional[int] = 10,
    service: VideoDubbingService = Depends(get_video_dubbing_service)
):
    """
    List recent dubbing requests.
    
    - **limit**: Maximum number of requests to return (default: 10)
    """
    try:
        # This would need to be implemented in the service
        # For now, return empty list
        return []
        
    except Exception as e:
        logger.error(f"List requests failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to list requests")


@router.delete("/request/{request_id}")
async def delete_dubbing_request(
    request_id: str,
    service: VideoDubbingService = Depends(get_video_dubbing_service)
):
    """
    Delete a dubbing request and associated files.
    
    - **request_id**: The ID of the dubbing request to delete
    """
    try:
        # This would need to be implemented in the service
        return JSONResponse(
            status_code=200,
            content={"message": "Request deletion not yet implemented"}
        )
        
    except Exception as e:
        logger.error(f"Delete request failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete request")


# Health check endpoint
@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "video-dubbing"}
