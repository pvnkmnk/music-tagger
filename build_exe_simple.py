#!/usr/bin/env python3
"""
Simplified build script that handles permission errors better
"""
import os
import sys
import shutil
import subprocess

def main():
    # Get the project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Working in directory: {project_dir}")
    
    # Define output directories - use user-friendly names to avoid permission issues
    dist_dir = os.path.join(project_dir, "dist")
    build_dir = os.path.join(project_dir, "build")
    
    # Clean directories if they exist - with better error handling
    for dir_path in [dist_dir, build_dir]:
        if os.path.exists(dir_path):
            print(f"Cleaning {dir_path}...")
            try:
                shutil.rmtree(dir_path)
                print(f"Successfully removed {dir_path}")
            except PermissionError:
                print(f"Permission error when removing {dir_path}")
                print("Try closing any applications that might be using files in this directory")
                print("Continuing without cleaning...")
            except Exception as e:
                print(f"Error cleaning {dir_path}: {str(e)}")
                print("Continuing without cleaning...")
    
    # Create a simple PyInstaller command
    pyinstaller_cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name=MusicTagger",
        "--onedir",
        "--windowed",
        "music_tagger_gui.py"
    ]
    
    print("\nRunning PyInstaller...")
    print(f"Command: {' '.join(pyinstaller_cmd)}")
    
    try:
        subprocess.run(pyinstaller_cmd, check=True)
        print("\nBuild completed!")
        print(f"Your executable is in: {os.path.join(dist_dir, 'MusicTagger')}")
        
        # Try to copy the core file if needed
        core_file = os.path.join(project_dir, "music_tagger.py")
        target_file = os.path.join(dist_dir, "MusicTagger", "music_tagger.py")
        if os.path.exists(core_file) and not os.path.exists(target_file):
            try:
                shutil.copy(core_file, target_file)
                print(f"Copied {core_file} to the distribution directory")
            except Exception as e:
                print(f"Warning: Could not copy {core_file}: {str(e)}")
                
        return 0
    except Exception as e:
        print(f"Error during build: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
