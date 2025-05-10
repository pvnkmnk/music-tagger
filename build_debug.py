#!/usr/bin/env python3
"""
Debug build script for Music Tagger GUI with additional error handling and diagnostics
"""
import os
import sys
import shutil
import subprocess
import time
import signal
import psutil  # You may need to install this: pip install psutil

def kill_running_executables():
    """Kill any running MusicTagger processes"""
    killed = False
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if 'MusicTagger' in proc.info['name']:
                print(f"Killing process: {proc.info['name']} (PID: {proc.info['pid']})")
                try:
                    proc.terminate()
                    killed = True
                except Exception as e:
                    print(f"Failed to kill process: {str(e)}")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    if killed:
        print("Waiting for processes to terminate...")
        time.sleep(2)  # Give processes time to terminate

def debug_importable_modules():
    """Check if key modules can be imported correctly"""
    modules_to_check = [
        "PyQt5", "PyQt5.QtWidgets", "PyQt5.QtCore", "PyQt5.QtGui",
        "watchdog", "watchdog.observers", "watchdog.events",
        "audio_utils", "mutagen"
    ]
    
    print("\nTesting module imports:")
    for module_name in modules_to_check:
        try:
            __import__(module_name)
            print(f"✓ Successfully imported {module_name}")
        except ImportError as e:
            print(f"✗ Failed to import {module_name}: {str(e)}")

def verify_code_files():
    """Verify key code files are correctly configured"""
    print("\nVerifying code files:")
    
    # Check audio_utils.py
    if os.path.exists("audio_utils.py"):
        with open("audio_utils.py", "r") as f:
            content = f.read()
            if "def is_audio_file" in content:
                print("✓ audio_utils.py contains the is_audio_file function")
            else:
                print("✗ is_audio_file function not found in audio_utils.py")
    else:
        print("✗ audio_utils.py file not found")
    
    # Check GUI imports
    with open("music_tagger_gui.py", "r") as f:
        content = f.read()
        if "from audio_utils import is_audio_file" in content:
            print("✓ music_tagger_gui.py correctly imports is_audio_file from audio_utils")
        else:
            print("✗ music_tagger_gui.py has incorrect imports for is_audio_file")

def build_executable_with_specs():
    """Build executable using more specific PyInstaller options"""
    print("\nBuilding executable with detailed specifications...")
    
    # Create spec file content for better control
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['music_tagger_gui.py'],
    pathex=[],
    binaries=[],
    datas=[('audio_utils.py', '.'), ('music_tagger.py', '.')],
    hiddenimports=['PyQt5', 'PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets', 
                   'watchdog', 'watchdog.observers', 'watchdog.events',
                   'audio_utils', 'mutagen'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MusicTagger',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MusicTagger',
)
"""
    
    # Write the spec file
    with open("music_tagger_gui_debug.spec", "w") as f:
        f.write(spec_content)
    
    # Run PyInstaller with the spec file
    command = [sys.executable, "-m", "PyInstaller", "music_tagger_gui_debug.spec", "--clean"]
    print(f"Running command: {' '.join(command)}")
    
    try:
        process = subprocess.Popen(
            command, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        
        # Print output in real time
        for line in process.stdout:
            print(line.strip())
        
        process.wait()
        return process.returncode == 0
    except Exception as e:
        print(f"Error running PyInstaller: {str(e)}")
        return False

def main():
    print("=== Music Tagger Debug Build ===")
    
    # Step 1: Kill any running executables
    try:
        kill_running_executables()
    except Exception as e:
        print(f"Error killing processes: {str(e)}")
        print("Continuing anyway...")
    
    # Step 2: Debug imports
    debug_importable_modules()
    
    # Step 3: Verify code files
    verify_code_files()
    
    # Step 4: Clean build directories if possible
    print("\nCleaning build directories...")
    for directory in ["dist", "build"]:
        try:
            if os.path.exists(directory):
                shutil.rmtree(directory)
                print(f"✓ Successfully cleaned {directory}")
            else:
                print(f"✓ {directory} doesn't exist, no cleaning needed")
        except Exception as e:
            print(f"✗ Failed to clean {directory}: {str(e)}")
    
    # Step 5: Build the executable with detailed specs
    success = build_executable_with_specs()
    
    if success:
        print("\n✅ Build completed successfully!")
        print("Your executable is in: dist/MusicTagger")
        
        # Copy the core files manually as a backup
        try:
            if not os.path.exists("dist/MusicTagger"):
                os.makedirs("dist/MusicTagger", exist_ok=True)
            
            for file in ["audio_utils.py", "music_tagger.py"]:
                if os.path.exists(file):
                    shutil.copy(file, f"dist/MusicTagger/{file}")
                    print(f"✓ Copied {file} to dist/MusicTagger")
        except Exception as e:
            print(f"Warning: Could not copy files: {str(e)}")
        
        return 0
    else:
        print("\n❌ Build failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
