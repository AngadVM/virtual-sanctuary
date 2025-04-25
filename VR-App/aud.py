from pydub import AudioSegment
import re

import os
import uuid
from pathlib import Path

def parse_timestamps(narration: str) -> list:
    """Extract (timestamp_ms, text) from narration."""
    segments = re.findall(r'\[(\d+:\d+:\d+)\]\s*(.*?)(?=\[|$)', narration, re.DOTALL)
    parsed = []
    for ts, text in segments:
        h, m, s = map(int, ts.split(':'))
        start_ms = (h*3600 + m*60 + s) * 1000
        parsed.append((start_ms, text.strip()))

    return parsed

def mix_narration(video_audio: AudioSegment, narration_segments: list, bg_music_path: str = None) -> AudioSegment:
    """Overlay TTS segments at specified timestamps."""
    # Overlay narration
    for start_ms, text in narration_segments:
        tts_audio = AudioSegment.silent(0)  # Replace with actual TTS
        tts_audio = AudioSegment.from_mp3(f"./Temp/tts_{uuid.uuid4()}.mp3")
        video_audio = video_audio.overlay(tts_audio, position=start_ms)
    
    # Add background music
    if bg_music_path and os.path.exists(bg_music_path):
        bg_music = AudioSegment.from_file(bg_music_path).fade_in(2000).fade_out(2000) - 10
        bg_music = bg_music[:len(video_audio)]
        video_audio = video_audio.overlay(bg_music)
    
    return video_audio
