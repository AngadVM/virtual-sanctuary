import os
import subprocess

def extract_audio(video_path: str) -> str:

    """Extract audio from video file."""
    temp_dir = "./Temp"

    os.makedirs(temp_dir, exist_ok=True)

    
    output_audio = f"{temp_dir}/extracted_audio_{os.path.basename(video_path)}.mp3"
    
    cmd = [
        "ffmpeg",
        "-i", video_path,
        "-vn",  # Skip video streams
        "-acodec", "libmp3lame",
        "-q:a", "2",
        output_audio,
        "-y"  # Overwrite if exists
    ]
    
    try:

        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError:
        # If extraction fails, create silent audio
        duration_cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            video_path
        ]
        
        try:
            result = subprocess.run(duration_cmd, capture_output=True, text=True, check=True)
            duration = float(result.stdout.strip())
        except Exception:
            duration = 60  # Default to 60 seconds if duration can't be determined
        
        # Create silent audio

        silent_cmd = [
            "ffmpeg",
            "-f", "lavfi",
            "-i", f"anullsrc=r=44100:cl=stereo:d={duration}",
            output_audio,
            "-y"
        ]
        subprocess.run(silent_cmd, check=True)

    
    return output_audio

def combine_video_audio(video_path: str, audio_path: str) -> str:
    """Combine video with new audio track while preserving VR metadata."""
    temp_dir = "./Temp"
    os.makedirs(temp_dir, exist_ok=True)
    
    output_video = f"{temp_dir}/narrated_{os.path.basename(video_path)}"
    
    # Get video metadata to preserve format
    probe_cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate,codec_name",
        "-of", "json",
        video_path
    ]
    
    try:
        result = subprocess.run(probe_cmd, capture_output=True, text=True, check=True)
        import json
        metadata = json.loads(result.stdout)
        video_stream = metadata.get('streams', [{}])[0]
        
        # Extract important info
        width = video_stream.get('width')
        height = video_stream.get('height')
        codec = video_stream.get('codec_name')
        
        # Get framerate as a number
        r_frame_rate = video_stream.get('r_frame_rate', '30/1')
        if '/' in r_frame_rate:
            num, den = map(int, r_frame_rate.split('/'))
            framerate = num/den if den else 30
        else:
            framerate = float(r_frame_rate)

            
        print(f"Preserving video format: {width}x{height} @{framerate}fps ({codec})")
    except Exception as e:
        print(f"Error getting video metadata: {e}")
        # Default to copy mode if metadata extraction fails
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-i", audio_path,
            "-c:v", "copy",  # Copy video stream without re-encoding
            "-c:a", "aac",
            "-b:a", "192k",
            "-map", "0:v:0",
            "-map", "1:a:0",
            output_video,
            "-y"
        ]
    else:
        # Use specific settings based on extracted metadata
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-i", audio_path,
            "-c:v", "copy",  # Still use copy to preserve VR metadata
            "-c:a", "aac",
            "-b:a", "192k",
            "-map", "0:v:0",
            "-map", "1:a:0",
            # Preserve all metadata
            "-map_metadata", "0",
            # Preserve spherical projection metadata
            "-movflags", "use_metadata_tags",
            output_video,
            "-y"
        ]
    
    subprocess.run(cmd, check=True)
    return output_video

def process_video(video_path: str, narration: str, bg_music_path: str = None) -> str:
    """Process video with narration and optional background music.
    
    Args:
        video_path: Path to original video
        narration: Text narration with timestamps
        bg_music_path: Optional path to background music
        
    Returns:

        Path to processed video
    """

    from audio import mix_narration
    
    # Extract audio from video
    video_audio_path = extract_audio(video_path)
    
    # Mix narration with video audio
    final_audio_path = mix_narration(video_audio_path, narration, bg_music_path)
    
    # Combine video with new audio
    output_video_path = combine_video_audio(video_path, final_audio_path)
    

    # Clean up intermediate audio files
    # Keep these for debugging
    # os.remove(video_audio_path)

    # os.remove(final_audio_path)
    
    return output_video_path
