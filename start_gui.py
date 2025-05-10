#!/usr/bin/env python3
"""
Music Tagger GUI Launcher
Cross-platform launcher script for the Music Tagger GUI application
"""
import sys
import subprocess
import os
import platform

def main():
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the GUI application script
    gui_script = os.path.join(script_dir, "music_tagger_gui.py")
    
    # Command to run the GUI application
    if platform.system() == "Windows":
        # On Windows, use pythonw.exe if available to hide the console window
        try:
            # Attempt to find pythonw.exe
            python_dir = os.path.dirname(sys.executable)
            pythonw_path = os.path.join(python_dir, "pythonw.exe")
            
            if os.path.exists(pythonw_path):
                cmd = [pythonw_path, gui_script]
            else:
                cmd = [sys.executable, gui_script]
        except Exception:
            # Fall back to regular python
            cmd = [sys.executable, gui_script]
    else:
        # On macOS and Linux, use the regular python executable
        cmd = [sys.executable, gui_script]
    
    # Add any command line arguments
    cmd.extend(sys.argv[1:])
    
    try:
        # Start the GUI application
        if platform.system() == "Windows":
            # On Windows, use CREATE_NO_WINDOW flag to hide console
            subprocess.Popen(cmd, creationflags=0x08000000)
        else:
            # On macOS and Linux
            subprocess.Popen(cmd)
    except Exception as e:
        print(f"Error starting GUI application: {str(e)}")
        input("Press Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()
