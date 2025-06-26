#!/usr/bin/env python3
"""
Example client for the Gemini Video Dubbing API
"""
import requests
import time
import json
from pathlib import Path
import argparse


class VideoDubbingClient:
    """Client for interacting with the Video Dubbing API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def upload_video(
        self, 
        video_path: str, 
        target_language: str = "en-US",
        voice_style: str = "natural",
        preserve_emotions: bool = True
    ) -> dict:
        """Upload a video for dubbing"""
        url = f"{self.base_url}/api/v1/dubbing/upload"
        
        with open(video_path, 'rb') as f:
            files = {'file': (Path(video_path).name, f, 'video/mp4')}
            data = {
                'target_language': target_language,
                'voice_style': voice_style,
                'preserve_emotions': preserve_emotions
            }
            
            response = self.session.post(url, files=files, data=data)
            response.raise_for_status()
            return response.json()
    
    def get_status(self, request_id: str) -> dict:
        """Get processing status"""
        url = f"{self.base_url}/api/v1/dubbing/status/{request_id}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    def download_audio(self, request_id: str, output_path: str) -> bool:
        """Download dubbed audio"""
        url = f"{self.base_url}/api/v1/dubbing/download/{request_id}"
        response = self.session.get(url)
        
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            return True
        return False
    
    def get_available_voices(self) -> list:
        """Get list of available voices"""
        url = f"{self.base_url}/api/v1/dubbing/voices"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    def custom_dubbing(self, request_data: dict) -> dict:
        """Create custom dubbing with specific configurations"""
        url = f"{self.base_url}/api/v1/dubbing/custom"
        response = self.session.post(url, json=request_data)
        response.raise_for_status()
        return response.json()
    
    def wait_for_completion(self, request_id: str, timeout: int = 1800) -> dict:
        """Wait for processing to complete"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status = self.get_status(request_id)
            
            print(f"Status: {status['status']}")
            if status.get('progress') is not None:
                print(f"Progress: {status['progress']:.1%}")
            
            if status['status'] == 'completed':
                return status
            elif status['status'] == 'failed':
                raise Exception(f"Processing failed: {status.get('error_message', 'Unknown error')}")
            
            time.sleep(5)  # Check every 5 seconds
        
        raise TimeoutError("Processing timeout")


def main():
    parser = argparse.ArgumentParser(description="Video Dubbing API Client")
    parser.add_argument("video_path", help="Path to video file")
    parser.add_argument("--output", "-o", default="dubbed_audio.wav", help="Output audio file")
    parser.add_argument("--language", "-l", default="en-US", help="Target language")
    parser.add_argument("--style", "-s", default="natural", help="Voice style")
    parser.add_argument("--base-url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--list-voices", action="store_true", help="List available voices")
    
    args = parser.parse_args()
    
    client = VideoDubbingClient(args.base_url)
    
    if args.list_voices:
        print("Available voices:")
        voices = client.get_available_voices()
        for voice in voices:
            print(f"  {voice['name']}: {voice['characteristics']}")
            print(f"    Recommended for: {', '.join(voice['recommended_for'])}")
            print()
        return
    
    print(f"Uploading video: {args.video_path}")
    upload_result = client.upload_video(
        args.video_path,
        target_language=args.language,
        voice_style=args.style
    )
    
    request_id = upload_result['request_id']
    print(f"Upload successful! Request ID: {request_id}")
    
    print("Waiting for processing to complete...")
    try:
        final_status = client.wait_for_completion(request_id)
        
        if final_status['status'] == 'completed':
            print("Processing completed!")
            
            # Show analysis results
            if 'video_analysis' in final_status:
                analysis = final_status['video_analysis']
                print(f"\nVideo Analysis:")
                print(f"  Duration: {analysis['duration']:.1f} seconds")
                print(f"  Speakers: {analysis['speaker_count']}")
                print(f"  Language: {analysis.get('language_detected', 'Unknown')}")
                
                if analysis['speakers']:
                    print(f"  Speaker details:")
                    for speaker in analysis['speakers']:
                        print(f"    - {speaker.get('name', 'Unknown')}")
            
            # Download the audio
            print(f"\nDownloading audio to: {args.output}")
            if client.download_audio(request_id, args.output):
                print("Download successful!")
            else:
                print("Download failed!")
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
