from pydub import AudioSegment
import os
import random
from pathlib import Path
import asyncio
import aiohttp
import tempfile
import uuid
import shutil

async def get_random_background_music(music_folder):
    """Get a random background music file from the specified folder"""
    audio_extensions = {'.mp3'}
    
    music_files = [
        str(f) for f in Path(music_folder).iterdir()
        if f.is_file() and f.suffix.lower() in audio_extensions
    ]
    
    if not music_files:
        raise ValueError(f"No audio files found in {music_folder}")
    
    return random.choice(music_files)

async def download_audio(url, save_path=None):
    """
    Download audio file from a URL and return the path
    If save_path is None, use a temporary file
    """
    if save_path is None:
        fd, save_path = tempfile.mkstemp(suffix=".mp3")
        os.close(fd)
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"Failed to download audio: {response.status}")
                
                with open(save_path, 'wb') as f:
                    f.write(await response.read())
        
        return save_path
    except Exception as e:
        print(f"Error downloading audio: {e}")
        return None

async def mix_audio(main_audio_path, animal_audio_path=None, background_music_path=None, output_path=None, 
                    animal_volume_reduction_db=0, background_volume_reduction_db=5, 
                    fade_duration_ms=3000):
    """
    Mix multiple audio sources with extensive debugging
    """
    if output_path is None:
        output_path = f"./Temp/Mixed/mixed_{uuid.uuid4().hex}.mp3"
    
    
    try:
        # Verify all input files exist
        if not os.path.isfile(main_audio_path):
            print(f"[ERROR] Main audio file does not exist: {main_audio_path}")
            return False, "Main audio file not found"
            
        if animal_audio_path and not os.path.isfile(animal_audio_path):
            print(f"[ERROR] Animal audio file does not exist: {animal_audio_path}")
            animal_audio_path = None
            
        if background_music_path and not os.path.isfile(background_music_path):
            print(f"[ERROR] Background music file does not exist: {background_music_path}")
            background_music_path = None
        
        # Load main audio
        main_audio = AudioSegment.from_file(main_audio_path)
        main_duration = len(main_audio)
        
        # Start with main audio
        combined = main_audio
        
        # If we have animal audio, process it
        if animal_audio_path:
            try:
                animal_audio = AudioSegment.from_file(animal_audio_path)
                
                # Loop animal audio if it's shorter than main audio
                if len(animal_audio) < main_duration:
                    times_to_loop = (main_duration // len(animal_audio)) + 1
                    animal_audio = animal_audio * times_to_loop
                
                # Trim to match main audio length
                animal_audio = animal_audio[:main_duration]
                
                # Adjust volume and add fade
                animal_audio = animal_audio - animal_volume_reduction_db
                animal_audio = animal_audio.fade_in(fade_duration_ms).fade_out(fade_duration_ms)
                
                # Overlay animal audio with main audio
                combined = main_audio.overlay(animal_audio)
            except Exception as e:
                combined = main_audio
        
        # If we have background music, process it
        if background_music_path:
            try:
                background = AudioSegment.from_file(background_music_path)
                
                # Loop background if it's shorter than main audio
                if len(background) < main_duration:
                    times_to_loop = (main_duration // len(background)) + 1
                    background = background * times_to_loop
                
                # Trim to match main audio length
                background = background[:main_duration]
                
                # Adjust volume and add fade
                background = background - background_volume_reduction_db
                background = background.fade_in(fade_duration_ms).fade_out(fade_duration_ms)
                
                # Overlay background with combined audio
                final_audio = combined.overlay(background)
            except Exception as e:
                final_audio = combined
        else:
            final_audio = combined
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Export the final audio
        final_audio.export(output_path, format=os.path.splitext(output_path)[1][1:])
        
        return True, output_path
        
    except Exception as e:
        return False, f"Error mixing audio: {str(e)}"
    

async def process_audio(narrative, audio_urls=None):
    """Process audio with detailed debugging for background music issues"""
    try:
        # Create necessary directories
        os.makedirs("./Temp/Normal", exist_ok=True)
        os.makedirs("./Temp/Mixed", exist_ok=True)
        os.makedirs("./Temp/Background", exist_ok=True)
        os.makedirs("./Temp/Animal", exist_ok=True)
        
        # Generate the main narrative audio
        from Modules.tts import speak
        await speak(narrative)
        main_audio_path = "./Temp/Normal/main.mp3"
        
        # Generate a unique filename for the output
        output_filename = f"mixed_{uuid.uuid4().hex}.mp3"
        output_path = f"./Temp/Mixed/{output_filename}"
        
        # Download animal sound if available
        animal_audio_path = None
        if audio_urls and len(audio_urls) > 0:
            for audio_data in audio_urls:
                if 'url' in audio_data and audio_data['url']:
                    animal_audio_path = await download_audio(audio_data['url'], f"./Temp/Animal/animal_{uuid.uuid4().hex}.mp3")
                    if animal_audio_path:
                        break
        
        # Check background music directory content
        bg_dir = "./Temp/Background"
        print(f"[DEBUG] Checking background music directory: {bg_dir}")
         
        # Get background music with direct file selection if needed
        background_music_path = None
        try:
            background_music_path = await get_random_background_music("./Temp/Background")
            if background_music_path:
                # Verify file exists
                if not os.path.isfile(background_music_path):
                    print(f"[ERROR] Background music file does not exist: {background_music_path}")
                    background_music_path = None
            else:
                
                # Try direct file selection as fallback if directory exists
                bg_dir_path = Path("./Temp/Background")
                if bg_dir_path.exists():
                    mp3_files = list(bg_dir_path.glob("*.mp3"))
                    if mp3_files:
                        background_music_path = str(mp3_files[0])
        except Exception as e:
            print(f"[ERROR] Error getting background music: {str(e)}")
        
        # Mix all available audio sources
        success, result = await mix_audio(
            main_audio_path=main_audio_path,
            animal_audio_path=animal_audio_path,
            background_music_path=background_music_path,
            output_path=output_path
        )
        
        if success:
            return output_filename
        else:
            print(f"[ERROR] Audio mixing failed: {result}, copying main audio instead")
            shutil.copy(main_audio_path, output_path)
            return output_filename
            
    except Exception as e:
        print(f"[ERROR] Error in process_audio: {str(e)}")
        return None