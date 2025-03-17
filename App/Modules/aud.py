from pydub import AudioSegment
import os
import random
from pathlib import Path

def get_random_background_music(music_folder):
   
    audio_extensions = {'.mp3'}
    
    
    music_files = [
        str(f) for f in Path(music_folder).iterdir()
        if f.is_file() and f.suffix.lower() in audio_extensions
    ]
    
    if not music_files:
        raise ValueError(f"No audio files found in {music_folder}")
    
    
    return random.choice(music_files)

def mix_with_background_music(main_audio_path, background_music_path, output_path, 
                            background_volume_reduction_db=7, 
                            fade_duration_ms=3000):

    try:
        
        main_audio = AudioSegment.from_file(main_audio_path)
        background = AudioSegment.from_file(background_music_path)
        
        
        if len(background) < len(main_audio):
            
            times_to_loop = (len(main_audio) // len(background)) + 1
            background = background * times_to_loop
        
        
        background = background[:len(main_audio)]
        
        
        background = background - background_volume_reduction_db
        
        
        background = background.fade_in(fade_duration_ms).fade_out(fade_duration_ms)
        
        
        combined = main_audio.overlay(background)
        
       
        combined.export(output_path, format=os.path.splitext(output_path)[1][1:])
        
        return True, "Audio mixing completed successfully!"
        
    except Exception as e:
        return False, f"Error mixing audio: {str(e)}"


def combine():

    main_audio = "./Temp/Normal/main.mp3"
    background_music_folder = "./Temp/Background"
    output_file = "./Temp/Mixed/mixed_output.mp3"
    
    try:
        
        random_background = get_random_background_music(background_music_folder)
        print(f"Selected background music: {random_background}")
        
        
        success, message = mix_with_background_music(
            main_audio,
            random_background,
            output_file,
            background_volume_reduction_db=10,
            fade_duration_ms=3000
        )
        
        print(message)
        
    except Exception as e:
        print(f"Error: {str(e)}")


import requests

def download_audio(url, save_path):
    """
    Download audio file from a URL
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        
        return True
    except Exception as e:
        print(f"Error downloading audio: {e}")
        return False


if __name__ == "__main__":
   
    combine()