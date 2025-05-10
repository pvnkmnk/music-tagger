import wave
import struct
import os
import time
import random

def create_valid_wav(output_folder, timestamp=None):
    """Create a valid WAV file for testing tagging"""
    
    # Create folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Generate a unique filename with timestamp and random number
    if timestamp is None:
        timestamp = int(time.time())
    random_num = random.randint(1000, 9999)
    filename = f"valid_wav_{timestamp}_{random_num}.wav"
    
    # Create the path
    output_path = os.path.join(output_folder, filename)
    
    # Create a valid WAV file
    # Parameters:
    # - 1 channel (mono)
    # - 2 bytes per sample (16 bits)
    # - 44100 Hz sample rate
    # - 0.5 seconds of silence
    
    sample_rate = 44100
    duration = 0.5  # seconds
    num_frames = int(sample_rate * duration)
    
    with wave.open(output_path, 'wb') as wav_file:
        # nchannels, sampwidth, framerate, nframes, comptype, compname
        wav_file.setparams((1, 2, sample_rate, num_frames, 'NONE', 'not compressed'))
        
        # Generate silent audio (all zeros)
        for i in range(num_frames):
            # Pack a single sample of silence (0) as a signed 16-bit value
            wav_file.writeframes(struct.pack('h', 0))
    
    print(f"Created valid WAV file: {output_path}")
    return output_path

if __name__ == "__main__":
    folder_path = input("Enter folder path for test WAV (default: C:\\Users\\twist\\Music\\JANUARYDECEMBER!): ") or "C:\\Users\\twist\\Music\\JANUARYDECEMBER!"
    create_valid_wav(folder_path)
