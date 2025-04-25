from pydub import AudioSegment
import re

import os
import uuid
import asyncio
import edge_tts

# Default voice
voice = 'en-CA-LiamNeural'

def parse_timestamps(narration: str) -> list:
    """Extract (timestamp_ms, text) from narration."""
    segments = re.findall(r'\[(\d+:\d+:\d+)\]\s*(.*?)(?=\[|$)', narration, re.DOTALL)
    parsed = []
    for ts, text in segments:
        h, m, s = map(int, ts.split(':'))
        start_ms = (h*3600 + m*60 + s) * 1000
        parsed.append((start_ms, text.strip()))
    return parsed

async def text_to_speech_async(text: str, output_path: str, selected_voice: str = None) -> str:
    """Convert text to speech using edge-tts asynchronously."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Use provided voice or default
    tts_voice = selected_voice if selected_voice else voice
    
    # Add adjustments for a more Attenborough-like delivery
    communicate = edge_tts.Communicate(text, tts_voice, rate="-15%", pitch="-5Hz", volume="+20%")

    await communicate.save(output_path)
    return output_path

def text_to_speech(text: str, output_path: str) -> str:
    """Synchronous wrapper for text_to_speech_async."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(text_to_speech_async(text, output_path, voice))
    finally:
        loop.close()

def mix_narration(video_audio_path: str, narration: str, bg_music_path: str = None) -> str:
    """Overlay TTS segments at specified timestamps without overlapping."""

    # Create temp directory if it doesn't exist
    temp_dir = "./Temp"
    normal_dir = os.path.join(temp_dir, "Normal")
    os.makedirs(normal_dir, exist_ok=True)
    
    # Load video audio
    video_audio = AudioSegment.from_file(video_audio_path)
    
    # Parse narration and sort by timestamp
    narration_segments = parse_timestamps(narration)
    narration_segments.sort(key=lambda x: x[0])  # Sort by timestamp
    
    # Create a new audio track for narration only
    narration_track = AudioSegment.silent(duration=len(video_audio))
    
    # Process each segment and add to narration track
    segment_end_times = []  # Track when each segment ends
    
    for i, (start_ms, text) in enumerate(narration_segments):
        # Generate TTS audio with a unique filename for each segment
        tts_file = f"{normal_dir}/segment_{i}_{uuid.uuid4()}.mp3"
        text_to_speech(text, tts_file)
        

        # Check if file was created

        if not os.path.exists(tts_file) or os.path.getsize(tts_file) == 0:
            raise Exception(f"Failed to generate TTS for segment: {text}")
            
        tts_audio = AudioSegment.from_mp3(tts_file)
        
        # Check for overlap with previous segments
        current_end_time = start_ms + len(tts_audio)
        
        # If this segment would overlap with any previous segment that's not yet finished,
        # we need to delay it until the previous segment finishes

        for prev_end in segment_end_times:
            if start_ms < prev_end:
                # This segment starts before a previous one ends - adjust start time
                start_ms = prev_end + 500  # Add 500ms buffer between segments
                current_end_time = start_ms + len(tts_audio)

                break

        
        # Add this segment's end time to our tracking list
        segment_end_times.append(current_end_time)
        

        # Add narration to the track at the (possibly adjusted) timestamp
        if start_ms + len(tts_audio) <= len(narration_track):
            narration_track = narration_track.overlay(tts_audio, position=start_ms)
        else:
            # If narration extends beyond video length, trim it
            tts_audio = tts_audio[:len(narration_track) - start_ms]
            narration_track = narration_track.overlay(tts_audio, position=start_ms)
    
    # Mix narration track with original audio
    # Keep original audio but reduce volume when narration is playing
    video_audio = video_audio - 5  # Reduce original audio by 5dB

    
    # Add narration on top
    final_audio = video_audio.overlay(narration_track)
    
    # Add background music if provided
    if bg_music_path and os.path.exists(bg_music_path):
        bg_music = AudioSegment.from_file(bg_music_path).fade_in(2000).fade_out(2000) - 15  # -15 dB (lower volume)
        
        # Loop music if too short

        if len(bg_music) < len(final_audio):
            loops_needed = len(final_audio) // len(bg_music) + 1
            bg_music = bg_music * loops_needed
        
        # Trim to match video length
        bg_music = bg_music[:len(final_audio)]
        
        # Overlay
        final_audio = final_audio.overlay(bg_music)
    
    # Export final audio
    output_path = f"{temp_dir}/final_audio_{uuid.uuid4()}.mp3"
    final_audio.export(output_path, format="mp3")
    

    return output_path
