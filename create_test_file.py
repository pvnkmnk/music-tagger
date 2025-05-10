import os
import time
import random

def create_sample_mp3(output_folder, timestamp=None):
    """Create a sample MP3 file in the specified folder with a timestamp in the filename"""
    # Create folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Generate a unique filename with timestamp and random number
    if timestamp is None:
        timestamp = int(time.time())
    random_num = random.randint(1000, 9999)
    filename = f"test_song_{timestamp}_{random_num}.mp3"
    
    # Create the path
    output_path = os.path.join(output_folder, filename)
    
    # Create an empty sample MP3 file
    with open(output_path, 'wb') as f:
        # ID3v2 tag header (simplest form)
        f.write(b'ID3\x03\x00\x00\x00\x00\x00\x02')
        # Some dummy MP3 frames content (not actually playable)
        f.write(b'\xff\xfb\x90\x04' * 1000)
    
    print(f"Created dummy MP3 file: {output_path}")
    return output_path

def create_sample_flac(output_folder, timestamp=None):
    """Create a sample FLAC file in the specified folder with a timestamp in the filename"""
    os.makedirs(output_folder, exist_ok=True)
    
    # Generate a unique filename with timestamp and random number
    if timestamp is None:
        timestamp = int(time.time())
    random_num = random.randint(1000, 9999)
    filename = f"test_song_{timestamp}_{random_num}.flac"
    
    output_path = os.path.join(output_folder, filename)
    
    # Create empty FLAC file with just the header
    with open(output_path, 'wb') as f:
        # FLAC marker + basic metadata
        f.write(b'fLaC\x00\x00\x00\x22' + b'\x00' * 34)
    
    print(f"Created dummy FLAC file: {output_path}")
    return output_path

def create_sample_wav(output_folder, timestamp=None):
    """Create a sample WAV file in the specified folder with a timestamp in the filename"""
    os.makedirs(output_folder, exist_ok=True)
    
    # Generate a unique filename with timestamp and random number
    if timestamp is None:
        timestamp = int(time.time())
    random_num = random.randint(1000, 9999)
    filename = f"test_song_{timestamp}_{random_num}.wav"
    
    output_path = os.path.join(output_folder, filename)
    
    # Create empty WAV file with just the header
    with open(output_path, 'wb') as f:
        # WAV header (RIFF + WAVE)
        f.write(b'RIFF\x24\x00\x00\x00WAVE')
        # Dummy data
        f.write(b'fmt \x10\x00\x00\x00\x01\x00\x01\x00\x22\x56\x00\x00\x44\xac\x00\x00\x02\x00\x10\x00')
        f.write(b'data\x00\x00\x00\x00')
    
    print(f"Created dummy WAV file: {output_path}")
    return output_path

def create_all_sample_files(output_folder):
    """Create all sample files in the specified folder"""
    # Use the same timestamp for all files to group them
    timestamp = int(time.time())
    
    # Create one file of each type with the same timestamp base
    return {
        'mp3': create_sample_mp3(output_folder, timestamp),
        'flac': create_sample_flac(output_folder, timestamp),
        'wav': create_sample_wav(output_folder, timestamp),
        # Add MIDI file with .mid extension
        'mid': create_sample_midi(output_folder, timestamp)
    }

def create_sample_midi(output_folder, timestamp=None):
    """Create a sample MIDI file in the specified folder with a timestamp in the filename"""
    os.makedirs(output_folder, exist_ok=True)
    
    # Generate a unique filename with timestamp and random number
    if timestamp is None:
        timestamp = int(time.time())
    random_num = random.randint(1000, 9999)
    filename = f"test_song_{timestamp}_{random_num}.mid"
    
    output_path = os.path.join(output_folder, filename)
    
    # Create empty MIDI file with just the header
    with open(output_path, 'wb') as f:
        # MIDI header
        f.write(b'MThd\x00\x00\x00\x06\x00\x01\x00\x01\x01\x00')
        # Add an empty track
        f.write(b'MTrk\x00\x00\x00\x04\x00\xFF\x2F\x00')
    
    print(f"Created dummy MIDI file: {output_path}")
    return output_path

if __name__ == "__main__":
    folder_path = input("Enter folder path to create test files (default: C:\\Users\\twist\\Music\\JANUARYDECEMBER!): ") or "C:\\Users\\twist\\Music\\JANUARYDECEMBER!"
    create_all_sample_files(folder_path)
