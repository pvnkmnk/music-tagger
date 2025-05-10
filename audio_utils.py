#!/usr/bin/env python3
"""
Utility functions for audio file handling
"""

def is_audio_file(file_path):
    """Check if file is an audio file we support"""
    supported_extensions = ['.mp3', '.flac', '.wav', '.mid', '.midi']
    return any(file_path.lower().endswith(ext) for ext in supported_extensions)
