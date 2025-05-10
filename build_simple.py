#!/usr/bin/env python3
"""
Simplified build script for Music Tagger GUI
"""
import os
import sys
import subprocess
import shutil
import platform
import site
from pathlib import Path

def get_python_info():
    """Get information about Python installation and components"""
    info = {
        'executable': sys.executable,
        'version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        'platform': platform.system(),
        'packages_dirs': site.getsitepackages(),
        'user_site': site.getusersitepackages(),
        'has_pyqt': False,
        'has_qtmaterial': False,
        'has_pyinstaller': False
    }
    
    # Check for installed packages
    try:
        import PyQt5
        info['has_pyqt'] = True
    except ImportError:
        pass
    
    try:
        import qt_material
        info['has_qtmaterial'] = True
    except ImportError:
        pass
    
    try:
        import PyInstaller
        info['has_pyinstaller'] = True
    except ImportError:
        pass
    
    return info

def main():
    # Get the project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("=== Music Tagger Simple Build Script ===")
    print(f"Project directory: {project_dir}")
    
    # Get Python information
    python_info = get_python_info()
    print("\nPython Information:")
    print(f"Python version: {python_info['version']}")
    print(f"Platform: {python_info['platform']}")
    print(f"PyQt5 available: {'Yes' if python_info['has_pyqt'] else 'No'}")
    print(f"Qt Material available: {'Yes' if python_info['has_qtmaterial'] else 'No'}")
    print(f"PyInstaller available: {'Yes' if python_info['has_pyinstaller'] else 'No'}")
    
    # Ensure config.ini.sample exists
    config_sample = os.path.join(project_dir, "config.ini.sample")
    if not os.path.exists(config_sample):
        print("Creating config.ini.sample...")
        with open(config_sample, 'w') as f:
            f.write("[MusicTagger]\nlog_level = INFO\n\n[Folders]\nC:\\Path\\To\\Your\\Music\\Folder = Artist Name\n")
    
    # Clean previous builds
    dist_dir = os.path.join(project_dir, "dist")
    build_dir = os.path.join(project_dir, "build")
    
    if os.path.exists(dist_dir):
        print(f"Cleaning {dist_dir}...")
        shutil.rmtree(dist_dir)
    
    if os.path.exists(build_dir):
        print(f"Cleaning {build_dir}...")
        shutil.rmtree(build_dir)
    
    # Create a basic PyInstaller command with all required dependencies
    pyinstaller_cmd = [
        sys.executable, 
        "-m", 
        "PyInstaller",
        "--name=MusicTagger",
        "--onedir",
        "--windowed",
        "--clean",
        "--hidden-import=PyQt5",
        "--hidden-import=PyQt5.QtCore",
        "--hidden-import=PyQt5.QtGui",
        "--hidden-import=PyQt5.QtWidgets",
        "--hidden-import=watchdog",
        "--hidden-import=watchdog.observers",
        "--hidden-import=watchdog.events",
        "--hidden-import=mutagen",
        "--hidden-import=tinytag",
        "--add-data", f"{config_sample};.",
        os.path.join(project_dir, "music_tagger_gui.py")
    ]
    
    # Add core files to include
    core_file = os.path.join(project_dir, "music_tagger.py")
    if os.path.exists(core_file):
        pyinstaller_cmd.extend(["--add-data", f"{core_file};."])
        
    # Check if qt-material is installed and include if available
    try:
        import importlib.util
        qt_material_spec = importlib.util.find_spec("qt_material")
        if qt_material_spec is not None:
            print("Including qt-material in the build...")
            pyinstaller_cmd.extend(["--hidden-import=qt_material"])
    except ImportError:
        pass
    
    # Ensure required packages are installed
    python_info = get_python_info()
    missing_packages = []
    
    if not python_info['has_pyinstaller']:
        missing_packages.append('pyinstaller')
    
    if not python_info['has_pyqt']:
        missing_packages.append('PyQt5')
    
    if not python_info['has_qtmaterial']:
        missing_packages.append('qt-material')
    
    # Install any missing packages
    if missing_packages:
        print(f"\nInstalling missing packages: {', '.join(missing_packages)}")
        for package in missing_packages:
            print(f"Installing {package}...")
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)
                print(f"{package} installed successfully")
            except Exception as e:
                print(f"Warning: Could not install {package}: {str(e)}")
                # Continue anyway, the build might still work
    
    # Run PyInstaller with updated path environment
    print("\nRunning PyInstaller...")
    print(f"Command: {' '.join(pyinstaller_cmd)}")
    
    # Use a custom environment that includes the updated PATH
    env = os.environ.copy()
    
    # Try to find the Scripts directory in user site-packages
    scripts_dirs = []
    for site_dir in site.getsitepackages():
        scripts_dir = os.path.join(site_dir, 'Scripts')
        if os.path.exists(scripts_dir):
            scripts_dirs.append(scripts_dir)
    
    user_site = site.getusersitepackages()
    if user_site:
        user_site_parent = Path(user_site).parent
        user_scripts = os.path.join(user_site_parent, 'Scripts')
        if os.path.exists(user_scripts):
            scripts_dirs.append(user_scripts)
    
    # Add Scripts directories to PATH
    if scripts_dirs:
        if 'PATH' in env:
            env['PATH'] = os.pathsep.join(scripts_dirs + [env['PATH']])
        else:
            env['PATH'] = os.pathsep.join(scripts_dirs)
    
    try:
        subprocess.run(pyinstaller_cmd, check=True, env=env)
        
        print("\nBuild completed successfully!")
        print(f"Output files can be found in: {os.path.join(dist_dir, 'MusicTagger')}")
        
        # Copy any additional files needed
        print("\nCopying additional files...")
        shutil.copy(os.path.join(project_dir, "music_tagger.py"), 
                   os.path.join(dist_dir, "MusicTagger"))
        
        # Create a README.txt
        with open(os.path.join(dist_dir, "MusicTagger", "README.txt"), 'w') as f:
            f.write("Music Tagger GUI\n")
            f.write("===============\n\n")
            f.write("This is the standalone executable version of Music Tagger.\n\n")
            f.write("To use:\n")
            f.write("1. Run MusicTagger.exe\n")
            f.write("2. Add folders to monitor and specify artist names\n")
            f.write("3. Click 'Start Monitoring'\n\n")
            f.write("The application can be minimized to the system tray.\n")
            f.write("\nThe application features a Material Design interface for a modern look and feel.\n")
        
        print("Done!")
        return 0
    except Exception as e:
        print(f"Error during build: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
