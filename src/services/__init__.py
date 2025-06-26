from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Tuple
from google import genai
from google.genai import types
import os
import asyncio
import logging
import wave
import tempfile
import time
from pathlib import Path
from src.entities import (
    VideoFile, DubbingRequest, DubbingResult, VideoAnalysis, 
    Speaker, VoiceName, ProcessingStatus, SpeakerType,
    CustomDubbingRequest, SpeakerConfiguration
)

logger = logging.getLogger(__name__)


class GeminiService:
    """Service for interacting with Google Gemini API"""
    
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        
    async def upload_video(self, file_path: str) -> Any:
        """Upload video to Gemini Files API"""
        try:
            uploaded_file = self.client.files.upload(file=file_path)
            logger.info(f"Video uploaded to Gemini: {uploaded_file.name}")
            
            # Wait for file to be processed
            max_wait_time = 60  # seconds
            wait_interval = 2   # seconds
            elapsed_time = 0
            
            while elapsed_time < max_wait_time:
                try:
                    # Check if file is ready by trying to get its metadata
                    file_info = self.client.files.get(name=uploaded_file.name)
                    if file_info.state == 'ACTIVE':
                        logger.info(f"File is ready for processing: {uploaded_file.name}")
                        return uploaded_file
                    elif file_info.state == 'FAILED':
                        raise Exception(f"File processing failed: {uploaded_file.name}")
                    
                    logger.info(f"File still processing, waiting... ({file_info.state})")
                    time.sleep(wait_interval)
                    elapsed_time += wait_interval
                    
                except Exception as e:
                    if elapsed_time == 0:  # First attempt failed
                        logger.warning(f"Could not check file status, proceeding anyway: {e}")
                        return uploaded_file
                    else:
                        time.sleep(wait_interval)
                        elapsed_time += wait_interval
            
            logger.warning(f"File processing timeout, proceeding anyway: {uploaded_file.name}")
            return uploaded_file
            
        except Exception as e:
            logger.error(f"Failed to upload video to Gemini: {e}")
            raise
    
    async def analyze_video(self, uploaded_file: Any) -> VideoAnalysis:
        """Analyze video to extract transcript, speakers, and metadata"""
        try:
            # Video analysis prompt with structured output
            analysis_prompt = """
            Analyze this video and provide detailed information about:
            1. Video duration in seconds
            2. Number of speakers (count distinct voices)
            3. Complete transcript with timestamps
            4. If multiple speakers, format as dialogue with speaker names
            5. Detected language
            
            For each speaker, identify:
            - Distinct voice characteristics
            - Emotional tone and style
            - Speaking segments with timestamps
            
            Transcribe the audio from this video, giving timestamps for salient events.
            Also provide visual descriptions and speaker analysis.
            """
            
            # Use structured output for better parsing
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[
                    uploaded_file,  # Use the file object directly
                    types.Part(text=analysis_prompt)
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema={
                        "type": "object",
                        "properties": {
                            "duration": {"type": "number"},
                            "speaker_count": {"type": "integer"},
                            "transcript": {"type": "string"},
                            "dialogue_format": {"type": "string"},
                            "language_detected": {"type": "string"},
                            "speakers": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "voice_characteristics": {"type": "string"},
                                        "emotional_tone": {"type": "string"},
                                        "dialogue_segments": {
                                            "type": "array",
                                            "items": {"type": "string"}
                                        },
                                        "timestamps": {
                                            "type": "array",
                                            "items": {
                                                "type": "array",
                                                "items": {"type": "number"}
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "required": ["duration", "speaker_count", "transcript"]
                    }
                )
            )
            
            analysis_data = response.parsed if hasattr(response, 'parsed') else eval(response.text)
            
            logger.info(f"Video analysis result: {analysis_data}")
            transcript = analysis_data.get('transcript', '')
            dialogue_format = analysis_data.get('dialogue_format')
            logger.info(f"Transcript length: {len(transcript)}, Dialogue format length: {len(dialogue_format) if dialogue_format else 0}")
            
            # Create Speaker objects
            speakers = []
            for i, speaker_data in enumerate(analysis_data.get('speakers', [])):
                speaker = Speaker(
                    name=speaker_data.get('name', f"Speaker_{i+1}"),
                    voice_name=self._suggest_voice_for_characteristics(
                        speaker_data.get('voice_characteristics', ''),
                        speaker_data.get('emotional_tone', '')
                    ),
                    dialogue_segments=speaker_data.get('dialogue_segments', []),
                    timestamps=speaker_data.get('timestamps', [])
                )
                speakers.append(speaker)
            
            return VideoAnalysis(
                duration=analysis_data.get('duration', 0.0),
                speaker_count=analysis_data.get('speaker_count', 1),
                speakers=speakers,
                transcript=analysis_data.get('transcript', ''),
                dialogue_format=analysis_data.get('dialogue_format'),
                language_detected=analysis_data.get('language_detected', 'en-US')
            )
            
        except Exception as e:
            logger.error(f"Failed to analyze video: {e}")
            raise
    
    def _suggest_voice_for_characteristics(self, characteristics: str, emotional_tone: str) -> VoiceName:
        """Suggest appropriate voice based on speaker characteristics"""
        # Simple heuristic for voice selection
        characteristics_lower = characteristics.lower()
        tone_lower = emotional_tone.lower()
        
        if 'deep' in characteristics_lower or 'male' in characteristics_lower:
            if 'authoritative' in tone_lower or 'firm' in tone_lower:
                return VoiceName.ORUS
            elif 'friendly' in tone_lower:
                return VoiceName.ACHIRD
            else:
                return VoiceName.KORE
        
        elif 'high' in characteristics_lower or 'female' in characteristics_lower:
            if 'bright' in tone_lower or 'cheerful' in tone_lower:
                return VoiceName.ZEPHYR
            elif 'gentle' in tone_lower:
                return VoiceName.VINDEMIATRIX
            else:
                return VoiceName.LEDA
        
        elif 'energetic' in tone_lower or 'excited' in tone_lower:
            return VoiceName.FENRIR
        elif 'calm' in tone_lower or 'smooth' in tone_lower:
            return VoiceName.ALGIEBA
        
        # Default voice
        return VoiceName.KORE
    
    async def generate_speech(
        self, 
        text: str, 
        speakers: List[Speaker], 
        target_language: str = "en-US",
        voice_style: str = "natural"
    ) -> bytes:
        """Generate speech from text using appropriate voices"""
        try:
            # Clean and validate the text
            if not text or not text.strip():
                raise ValueError("Text cannot be empty")
            
            text = text.strip()
            
            # Don't add unnecessary intro text - use the content directly
            logger.info(f"Final text for TTS (length: {len(text)}): {text[:100]}...")
            
            if len(speakers) == 1:
                return await self._generate_single_speaker_speech(
                    text, speakers[0], target_language, voice_style
                )
            else:
                try:
                    return await self._generate_multi_speaker_speech(
                        text, speakers, target_language, voice_style
                    )
                except Exception as multi_error:
                    logger.warning(f"Multi-speaker TTS failed: {multi_error}")
                    logger.info("Falling back to single-speaker TTS with first speaker")
                    return await self._generate_single_speaker_speech(
                        text, speakers[0], target_language, voice_style
                    )
        except Exception as e:
            logger.error(f"Failed to generate speech: {e}")
            raise
    
    async def _generate_single_speaker_speech(
        self, 
        text: str, 
        speaker: Speaker, 
        target_language: str,
        voice_style: str
    ) -> bytes:
        """Generate single speaker audio using correct Gemini API format"""
        try:
            # Use the text directly without additional formatting
            formatted_text = text
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash-preview-tts",
                contents=[
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_text(text=formatted_text)
                        ]
                    )
                ],
                config=types.GenerateContentConfig(
                    temperature=1.0,
                    response_modalities=["audio"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name=speaker.voice_name.value
                            )
                        )
                    )
                )
            )
            
            logger.info(f"Single-speaker TTS Response: {response}")
            
            if (response.candidates and 
                response.candidates[0].content and 
                response.candidates[0].content.parts and
                response.candidates[0].content.parts[0].inline_data):
                
                inline_data = response.candidates[0].content.parts[0].inline_data
                audio_data = inline_data.data
                mime_type = inline_data.mime_type
                
                # Convert to WAV if needed
                if "L16" in mime_type or "pcm" in mime_type:
                    audio_data = self._convert_to_wav(audio_data, mime_type)
                
                logger.info(f"Generated single-speaker audio: {len(audio_data)} bytes")
                return audio_data
            else:
                raise Exception(f"No audio data in single-speaker TTS response: {response}")
                
        except Exception as e:
            logger.error(f"Failed to generate single-speaker speech: {e}")
            raise
    
    async def _generate_multi_speaker_speech(
        self, 
        text: str, 
        speakers: List[Speaker], 
        target_language: str,
        voice_style: str
    ) -> bytes:
        """Generate multi-speaker audio using correct Gemini API format"""
        try:
            # Use the text directly without additional formatting
            formatted_text = text
            
            # Don't add extra instructions - just use the content
            enhanced_prompt = formatted_text
            
            # Create speaker voice configs (limit to 2 speakers as supported by Gemini)
            speaker_voice_configs = []
            for speaker in speakers[:2]:  # Gemini supports max 2 speakers
                speaker_voice_configs.append(
                    types.SpeakerVoiceConfig(
                        speaker=speaker.name,
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name=speaker.voice_name.value
                            )
                        )
                    )
                )
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash-preview-tts",
                contents=[
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_text(text=enhanced_prompt)
                        ]
                    )
                ],
                config=types.GenerateContentConfig(
                    temperature=1.0,
                    response_modalities=["audio"],
                    speech_config=types.SpeechConfig(
                        multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                            speaker_voice_configs=speaker_voice_configs
                        )
                    )
                )
            )
            
            logger.info(f"Multi-speaker TTS Response: {response}")
            
            if (response.candidates and 
                response.candidates[0].content and 
                response.candidates[0].content.parts and
                response.candidates[0].content.parts[0].inline_data):
                
                inline_data = response.candidates[0].content.parts[0].inline_data
                audio_data = inline_data.data
                mime_type = inline_data.mime_type
                
                # Convert to WAV if needed
                if "L16" in mime_type or "pcm" in mime_type:
                    audio_data = self._convert_to_wav(audio_data, mime_type)
                
                logger.info(f"Generated multi-speaker audio: {len(audio_data)} bytes")
                return audio_data
            else:
                raise Exception(f"No audio data in multi-speaker TTS response: {response}")
                
        except Exception as e:
            logger.error(f"Failed to generate multi-speaker speech: {e}")
            raise
        
        raise ValueError(f"Unexpected multi-speaker TTS response structure: {response}")
    
    def _convert_to_wav(self, audio_data: bytes, mime_type: str) -> bytes:
        """Convert raw audio data to WAV format"""
        try:
            import struct
            
            # Parse audio parameters from mime type
            parameters = self._parse_audio_mime_type(mime_type)
            bits_per_sample = parameters["bits_per_sample"]
            sample_rate = parameters["rate"]
            num_channels = 1
            data_size = len(audio_data)
            bytes_per_sample = bits_per_sample // 8
            block_align = num_channels * bytes_per_sample
            byte_rate = sample_rate * block_align
            chunk_size = 36 + data_size  # 36 bytes for header fields before data chunk size

            # Create WAV header
            header = struct.pack(
                "<4sI4s4sIHHIIHH4sI",
                b"RIFF",          # ChunkID
                chunk_size,       # ChunkSize (total file size - 8 bytes)
                b"WAVE",          # Format
                b"fmt ",          # Subchunk1ID
                16,               # Subchunk1Size (16 for PCM)
                1,                # AudioFormat (1 for PCM)
                num_channels,     # NumChannels
                sample_rate,      # SampleRate
                byte_rate,        # ByteRate
                block_align,      # BlockAlign
                bits_per_sample,  # BitsPerSample
                b"data",          # Subchunk2ID
                data_size         # Subchunk2Size (size of audio data)
            )
            return header + audio_data
        except Exception as e:
            logger.error(f"Failed to convert audio to WAV: {e}")
            return audio_data  # Return original data if conversion fails

    def _parse_audio_mime_type(self, mime_type: str) -> dict:
        """Parse bits per sample and rate from an audio MIME type string"""
        bits_per_sample = 16
        rate = 24000

        # Extract rate from parameters
        parts = mime_type.split(";")
        for param in parts:
            param = param.strip()
            if param.lower().startswith("rate="):
                try:
                    rate_str = param.split("=", 1)[1]
                    rate = int(rate_str)
                except (ValueError, IndexError):
                    pass  # Keep rate as default
            elif param.startswith("audio/L"):
                try:
                    bits_per_sample = int(param.split("L", 1)[1])
                except (ValueError, IndexError):
                    pass  # Keep bits_per_sample as default

        return {"bits_per_sample": bits_per_sample, "rate": rate}

    async def get_file(self, file_uri: str) -> Any:
        """Get file object from Gemini Files API by URI"""
        try:
            file_obj = self.client.files.get(name=file_uri)
            logger.info(f"Retrieved file from Gemini: {file_uri}")
            return file_obj
        except Exception as e:
            logger.error(f"Failed to get file from Gemini: {e}")
            raise

    async def delete_file(self, file_uri: str):
        """Delete file from Gemini Files API"""
        try:
            self.client.files.delete(name=file_uri)
            logger.info(f"Deleted file from Gemini: {file_uri}")
        except Exception as e:
            logger.error(f"Failed to delete file from Gemini: {e}")


class FileService:
    """Service for file operations"""
    
    def __init__(self, upload_dir: str = "uploads", output_dir: str = "outputs"):
        self.upload_dir = Path(upload_dir)
        self.output_dir = Path(output_dir)
        self.upload_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
    
    async def save_uploaded_file(self, file_content: bytes, filename: str) -> str:
        """Save uploaded file and return file path"""
        file_path = self.upload_dir / filename
        with open(file_path, 'wb') as f:
            f.write(file_content)
        logger.info(f"Saved uploaded file: {file_path}")
        return str(file_path)
    
    async def save_audio_file(self, audio_data: bytes, filename: str) -> str:
        """Save generated audio file"""
        file_path = self.output_dir / filename
        
        # The audio_data from Gemini TTS is already WAV format, just save it directly
        with open(str(file_path), "wb") as f:
            f.write(audio_data)
        
        logger.info(f"Saved audio file: {file_path}")
        return str(file_path)
    
    async def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get file information"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        stat = path.stat()
        return {
            "size": stat.st_size,
            "mime_type": self._get_mime_type(path.suffix),
            "exists": True
        }
    
    def _get_mime_type(self, extension: str) -> str:
        """Get MIME type from file extension"""
        mime_types = {
            '.mp4': 'video/mp4',
            '.avi': 'video/avi',
            '.mov': 'video/mov',
            '.webm': 'video/webm',
            '.wav': 'audio/wav',
            '.mp3': 'audio/mpeg'
        }
        return mime_types.get(extension.lower(), 'application/octet-stream')


class VideoDubbingService:
    """Main service for video dubbing operations"""
    
    def __init__(
        self, 
        gemini_service: GeminiService,
        file_service: FileService,
        video_repo,
        request_repo,
        result_repo
    ):
        self.gemini_service = gemini_service
        self.file_service = file_service
        self.video_repo = video_repo
        self.request_repo = request_repo
        self.result_repo = result_repo
    
    async def process_video_upload(
        self, 
        file_content: bytes, 
        filename: str,
        target_language: str = "en-US",
        voice_style: str = "natural",
        preserve_emotions: bool = True
    ) -> DubbingResult:
        """Process uploaded video and start dubbing"""
        try:
            # Save uploaded file
            file_path = await self.file_service.save_uploaded_file(file_content, filename)
            file_info = await self.file_service.get_file_info(file_path)
            
            # Create video file entity
            video_file = VideoFile(
                filename=filename,
                file_path=file_path,
                file_size=file_info["size"],
                mime_type=file_info["mime_type"]
            )
            
            # Save video file
            await self.video_repo.save(video_file)
            
            # Create dubbing request
            dubbing_request = DubbingRequest(
                video_file=video_file,
                target_language=target_language,
                voice_style=voice_style,
                preserve_emotions=preserve_emotions
            )
            
            # Save dubbing request
            await self.request_repo.save(dubbing_request)
            
            # Create initial result
            result = DubbingResult(
                request_id=dubbing_request.id,
                status=ProcessingStatus.PENDING
            )
            await self.result_repo.save(result)
            
            # Start async processing
            asyncio.create_task(self._process_dubbing_async(dubbing_request, result))
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to process video upload: {e}")
            raise
    
    async def _process_dubbing_async(self, request: DubbingRequest, result: DubbingResult):
        """Async processing of dubbing request"""
        try:
            # Update status to processing
            await self.result_repo.update_status(result.id, ProcessingStatus.PROCESSING.value)
            
            # Upload to Gemini
            uploaded_file = await self.gemini_service.upload_video(request.video_file.file_path)
            
            # Update video file with Gemini URI
            request.video_file.gemini_file_uri = uploaded_file.name if hasattr(uploaded_file, 'name') else str(uploaded_file)
            await self.video_repo.save(request.video_file)
            
            # Analyze video
            analysis = await self.gemini_service.analyze_video(uploaded_file)
            
            # Generate speech
            # Use the full transcript, not just dialogue_format flag
            text_to_speech = analysis.transcript
            logger.info(f"Text being sent to TTS (length: {len(text_to_speech)}): {text_to_speech[:200]}...")
            
            # Clean up the text - remove timestamps if present
            if text_to_speech and any(timestamp in text_to_speech for timestamp in ['00:', '[Music]']):
                # Extract just the spoken content, removing timestamps and music markers
                lines = text_to_speech.split('\n')
                clean_lines = []
                for line in lines:
                    # Remove timestamp patterns like "00:00" and "[Music]"
                    import re
                    cleaned = re.sub(r'\d{2}:\d{2}\s*', '', line)
                    cleaned = re.sub(r'\[Music\]\s*', '', cleaned)
                    cleaned = cleaned.strip()
                    if cleaned and not cleaned.isspace():
                        clean_lines.append(cleaned)
                text_to_speech = ' '.join(clean_lines)
            
            logger.info(f"Cleaned text for TTS (length: {len(text_to_speech)}): {text_to_speech[:200]}...")
            
            audio_data = await self.gemini_service.generate_speech(
                text_to_speech,
                analysis.speakers,
                request.target_language,
                request.voice_style
            )
            
            # Save audio file
            audio_filename = f"dubbed_{request.video_file.filename}.wav"
            audio_path = await self.file_service.save_audio_file(audio_data, audio_filename)
            
            # Update result with success
            await self.result_repo.update_status(
                result.id,
                ProcessingStatus.COMPLETED.value,
                video_analysis=analysis.model_dump(),
                audio_file_path=audio_path
            )
            
            # Clean up Gemini file
            file_uri = uploaded_file.name if hasattr(uploaded_file, 'name') else str(uploaded_file)
            await self.gemini_service.delete_file(file_uri)
            
        except Exception as e:
            logger.error(f"Dubbing processing failed: {e}")
            await self.result_repo.update_status(
                result.id,
                ProcessingStatus.FAILED.value,
                error_message=str(e)
            )
    
    async def get_dubbing_status(self, request_id: str) -> Optional[DubbingResult]:
        """Get dubbing processing status"""
        return await self.result_repo.get_by_request_id(request_id)
    
    async def process_custom_dubbing(
        self, 
        custom_request: CustomDubbingRequest
    ) -> DubbingResult:
        """Process custom dubbing with user-defined speaker configurations"""
        try:
            # Get existing video file
            video_file = await self.video_repo.get_by_id(custom_request.video_id)
            if not video_file:
                raise ValueError(f"Video not found: {custom_request.video_id}")
            
            # Create new dubbing request
            dubbing_request = DubbingRequest(
                video_file=video_file,
                target_language=custom_request.target_language,
                voice_style=custom_request.global_voice_style
            )
            await self.request_repo.save(dubbing_request)
            
            # Create result
            result = DubbingResult(
                request_id=dubbing_request.id,
                status=ProcessingStatus.PENDING
            )
            await self.result_repo.save(result)
            
            # Start async processing with custom configurations
            asyncio.create_task(
                self._process_custom_dubbing_async(dubbing_request, result, custom_request)
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to process custom dubbing: {e}")
            raise
    
    async def _process_custom_dubbing_async(
        self, 
        request: DubbingRequest, 
        result: DubbingResult,
        custom_request: CustomDubbingRequest
    ):
        """Async processing of custom dubbing request"""
        try:
            await self.result_repo.update_status(result.id, ProcessingStatus.PROCESSING.value)
            
            # Get existing analysis or create new one
            if not request.video_file.gemini_file_uri:
                uploaded_file = await self.gemini_service.upload_video(request.video_file.file_path)
                request.video_file.gemini_file_uri = uploaded_file.name if hasattr(uploaded_file, 'name') else str(uploaded_file)
                await self.video_repo.save(request.video_file)
            else:
                uploaded_file = await self.gemini_service.get_file(request.video_file.gemini_file_uri)
            
            analysis = await self.gemini_service.analyze_video(uploaded_file)
            
            # Apply custom speaker configurations
            for i, speaker_config in enumerate(custom_request.speaker_configurations):
                if i < len(analysis.speakers):
                    analysis.speakers[i].name = speaker_config.speaker_name
                    analysis.speakers[i].voice_name = speaker_config.voice_name
            
            # Generate speech with custom configurations
            # Use the full transcript, properly cleaned
            text_to_speech = analysis.transcript
            
            # Clean up the text - remove timestamps if present
            if text_to_speech and any(timestamp in text_to_speech for timestamp in ['00:', '[Music]']):
                # Extract just the spoken content, removing timestamps and music markers
                lines = text_to_speech.split('\n')
                clean_lines = []
                for line in lines:
                    # Remove timestamp patterns like "00:00" and "[Music]"
                    import re
                    cleaned = re.sub(r'\d{2}:\d{2}\s*', '', line)
                    cleaned = re.sub(r'\[Music\]\s*', '', cleaned)
                    cleaned = cleaned.strip()
                    if cleaned and not cleaned.isspace():
                        clean_lines.append(cleaned)
                text_to_speech = ' '.join(clean_lines)
            
            audio_data = await self.gemini_service.generate_speech(
                text_to_speech,
                analysis.speakers,
                request.target_language,
                request.voice_style
            )
            
            # Save audio file
            audio_filename = f"custom_dubbed_{request.video_file.filename}.wav"
            audio_path = await self.file_service.save_audio_file(audio_data, audio_filename)
            
            # Update result
            await self.result_repo.update_status(
                result.id,
                ProcessingStatus.COMPLETED.value,
                video_analysis=analysis.model_dump(),
                audio_file_path=audio_path
            )
            
        except Exception as e:
            logger.error(f"Custom dubbing processing failed: {e}")
            await self.result_repo.update_status(
                result.id,
                ProcessingStatus.FAILED.value,
                error_message=str(e)
            )
