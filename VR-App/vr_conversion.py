import os
import subprocess
import uuid
import tempfile
from typing import Tuple, List

def convert_to_360(video_path: str, projection_type: str = "equirectangular", fov: int = 180) -> str:
    """
    Convert standard video to YouTube-compatible 360° format
    
    Args:

        video_path: Path to input video
        projection_type: Type of 360 projection (equirectangular is YouTube standard)
        fov: Field of view in degrees
        
    Returns:
        Path to YouTube-compatible 360° video
    """
    temp_dir = "./Temp"

    os.makedirs(temp_dir, exist_ok=True)

    
    output_video = f"{temp_dir}/YT360_{os.path.basename(video_path)}"
    
    # Get video dimensions
    probe_cmd = [

        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "csv=p=0",
        video_path
    ]
    
    result = subprocess.run(probe_cmd, capture_output=True, text=True, check=True)
    width, height = map(int, result.stdout.strip().split(','))
    
    # For YouTube 360, recommended resolutions are:
    # - 7680×3840 (8K)
    # - 3840×1920 (4K)
    # - 2560×1280 (2.5K)
    
    # Select appropriate resolution based on input size
    if width * height >= 4000000:  # If input is roughly 4K or higher
        target_height = 1920
        target_width = 3840

    else:
        target_height = 1280
        target_width = 2560
    
    # YouTube requires equirectangular projection for 360 videos
    if projection_type.lower() != "equirectangular":
        print(f"Warning: Converting to equirectangular projection for YouTube compatibility")

        projection_type = "equirectangular"
    
    # Use v360 filter to convert to equirectangular format with YouTube specs
    cmd = [
        "ffmpeg",

        "-i", video_path,
        "-vf", f"v360=input=flat:output=equirect:ih_fov={fov}:iv_fov={fov}:w={target_width}:h={target_height}",
        "-c:v", "libx264",

        "-preset", "slow",  # Higher quality for YouTube
        "-crf", "18",       # Higher quality (lower value)

        "-c:a", "aac",      # YouTube recommended audio codec

        "-b:a", "192k",     # Good audio bitrate
        # Add YouTube-compatible VR metadata
        "-metadata:s:v:0", "spherical=true",
        "-metadata:s:v:0", "stereo=monoscopic",
        "-metadata:s:v:0", "projection=equirectangular",
        # Add specific YouTube spatial media metadata using Google's format
        "-movflags", "+faststart",  # Optimize for web streaming
        output_video,
        "-y"
    ]
    
    subprocess.run(cmd, check=True)
    
    # Verify the video has the correct metadata
    print(f"Created YouTube 360° compatible video: {output_video}")
    print(f"Resolution: {target_width}x{target_height}, Projection: equirectangular")
    

    return output_video

def create_dual_video(left_path: str, right_path: str) -> str:
    """
    Create stereoscopic VR video from two input videos (left and right eye)
    For YouTube, this should be top-bottom format for 3D 360 videos
    
    Args:

        left_path: Path to left eye video
        right_path: Path to right eye video

        
    Returns:
        Path to YouTube-compatible stereoscopic VR video
    """
    temp_dir = "./Temp"
    os.makedirs(temp_dir, exist_ok=True)
    
    output_video = f"{temp_dir}/YT360_3D_{uuid.uuid4()}.mp4"
    
    # For YouTube 3D 360, top-bottom format is recommended
    cmd = [
        "ffmpeg",
        "-i", left_path,
        "-i", right_path,
        "-filter_complex", "vstack=inputs=2",  # Stack vertically for top-bottom format
        "-c:v", "libx264",
        "-preset", "slow",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        # Add YouTube-compatible VR metadata for stereoscopic
        "-metadata:s:v:0", "spherical=true",
        "-metadata:s:v:0", "stereo=top-bottom",  # YouTube prefers top-bottom for 3D
        "-metadata:s:v:0", "projection=equirectangular",
        "-movflags", "+faststart",
        output_video,
        "-y"
    ]
    
    subprocess.run(cmd, check=True)
    return output_video

def generate_vr_scene(background_color: str = "black", 
                      objects: List[Tuple[str, int, int, int, int]] = None) -> str:
    """
    Generate a YouTube-compatible 360° VR scene
    
    Args:
        background_color: Color of the background
        objects: List of (image_path, x, y, width, height) for objects to place
        
    Returns:
        Path to YouTube-compatible 360° video
    """
    temp_dir = "./Temp"
    os.makedirs(temp_dir, exist_ok=True)
    
    # Create equirectangular video with YouTube recommended resolution (4K)

    output_video = f"{temp_dir}/YT360_scene_{uuid.uuid4()}.mp4"

    
    # Base command to create background
    cmd = [
        "ffmpeg",
        "-f", "lavfi", 
        "-i", f"color=c={background_color}:s=3840x1920:d=10:r=30",  # 4K resolution, 30fps
    ]
    
    filter_complex = []

    input_count = 1
    
    # Add each object to the scene
    if objects:
        for idx, (img_path, x, y, width, height) in enumerate(objects):

            # Add input for this object
            cmd.extend(["-i", img_path])
            
            # Calculate position in equirectangular coordinates
            filter_complex.append(f"[{input_count}]scale={width}:{height}[obj{idx}];")
            filter_complex.append(f"[0][obj{idx}]overlay=x={x}:y={y}:shortest=1[bg{idx}];")
            
            # Update background reference
            if idx < len(objects) - 1:
                filter_complex[-1] = filter_complex[-1].replace(f"[bg{idx}];", f"[bg{idx}]")
            else:
                # For the last item, output to final video
                filter_complex[-1] = filter_complex[-1].replace(f"[bg{idx}];", f"[v]")

            
            input_count += 1

    else:
        # No objects, just use background
        filter_complex = ["[0]null[v]"]

    
    # Add filter complex to command
    if filter_complex:
        cmd.extend(["-filter_complex", "".join(filter_complex)])
    
    # Complete the command with YouTube-compatible settings
    cmd.extend([
        "-map", "[v]", 
        "-c:v", "libx264",
        "-preset", "slow",
        "-crf", "18",
        # Add YouTube 360 metadata
        "-metadata:s:v:0", "spherical=true",

        "-metadata:s:v:0", "stereo=monoscopic",
        "-metadata:s:v:0", "projection=equirectangular",
        "-movflags", "+faststart",
        output_video,
        "-y"
    ])
    

    subprocess.run(cmd, check=True)
    return output_video
