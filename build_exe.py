#!/usr/bin/env python3
"""
Build script for creating a standalone executable and installer for Music Tagger
"""
import os
import sys
import shutil
import subprocess
import platform
import datetime
import argparse

def banner(text):
    """Print a banner with the text"""
    print("\n" + "=" * 60)
    print(f" {text}")
    print("=" * 60)

def run_command(command, cwd=None):
    """Run a command and print output in real time"""
    print(f"Running: {' '.join(command)}")
    try:
        process = subprocess.Popen(
            command,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            shell=True if platform.system() == "Windows" else False
        )
        
        # Print output in real time
        for line in process.stdout:
            print(line, end='')
            
        process.wait()
        return process.returncode == 0
    except Exception as e:
        print(f"Error running command: {str(e)}")
        return False

def build_executable():
    """Build the executable using PyInstaller"""
    banner("Building executable with PyInstaller")
    
    # Get base directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Ensure PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller not found. Installing...")
        success = run_command([sys.executable, "-m", "pip", "install", "pyinstaller"])
        if not success:
            print("Failed to install PyInstaller")
            return False
    
    # Ensure qt-material is installed
    try:
        import qt_material
    except ImportError:
        print("qt-material not found. Installing...")
        success = run_command([sys.executable, "-m", "pip", "install", "qt-material"])
        if not success:
            print("Failed to install qt-material")
            print("Continuing anyway as it's optional. The app will use default styling.")
    
    # Clean previous build if it exists
    dist_dir = os.path.join(base_dir, "dist")
    build_dir = os.path.join(base_dir, "build")
    
    if os.path.exists(dist_dir):
        print(f"Cleaning previous build in {dist_dir}")
        shutil.rmtree(dist_dir, ignore_errors=True)
    
    if os.path.exists(build_dir):
        print(f"Cleaning previous build in {build_dir}")
        shutil.rmtree(build_dir, ignore_errors=True)
    
    # Build the executable
    success = run_command([
        sys.executable, 
        "-m", "PyInstaller", 
        "music_tagger_gui.spec", 
        "--clean"
    ], cwd=base_dir)
    
    if success:
        print("\nExecutable built successfully!")
        # Copy additional files needed
        print("Copying additional files...")
        try:
            # Copy the core music_tagger.py to the dist folder
            shutil.copy(
                os.path.join(base_dir, "music_tagger.py"),
                os.path.join(dist_dir, "MusicTagger")
            )
            # Copy config sample if not already included
            config_sample = os.path.join(base_dir, "config.ini.sample")
            if os.path.exists(config_sample):
                shutil.copy(
                    config_sample,
                    os.path.join(dist_dir, "MusicTagger")
                )
        except Exception as e:
            print(f"Warning: Error copying additional files: {str(e)}")
            
        # Create a README in the dist folder
        try:
            with open(os.path.join(dist_dir, "MusicTagger", "README.txt"), 'w') as f:
                f.write("Music Tagger GUI\n")
                f.write("===============\n\n")
                f.write("This is the standalone executable version of Music Tagger.\n\n")
                f.write("To use:\n")
                f.write("1. Run MusicTagger.exe\n")
                f.write("2. Add folders to monitor and specify artist names\n")
                f.write("3. Click 'Start Monitoring'\n\n")
                f.write("The application can be minimized to the system tray.\n")
        except Exception as e:
            print(f"Warning: Error creating README: {str(e)}")
            
        return True
    else:
        print("Failed to build executable")
        return False

def create_installer():
    """Create an installer using NSIS if available"""
    banner("Creating installer with NSIS")
    
    if platform.system() != "Windows":
        print("Installer creation is only supported on Windows")
        return False
    
    # Check if NSIS is installed
    nsis_paths = [
        r"C:\Program Files (x86)\NSIS\makensis.exe",
        r"C:\Program Files\NSIS\makensis.exe"
    ]
    
    nsis_path = None
    for path in nsis_paths:
        if os.path.exists(path):
            nsis_path = path
            break
    
    if not nsis_path:
        print("NSIS not found. Please install it from https://nsis.sourceforge.io/Download")
        print("Skipping installer creation")
        return False
    
    # Create NSIS script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    nsis_script = os.path.join(base_dir, "installer.nsi")
    
    # Get version and timestamp
    version = "1.0.0"  # You can get this dynamically if needed
    timestamp = datetime.datetime.now().strftime("%Y%m%d")
    
    try:
        with open(nsis_script, 'w') as f:
            f.write(f"""!define APPNAME "Music Tagger"
!define COMPANYNAME "JanuaryDecember"
!define DESCRIPTION "Automatic music file tagger with Material Design"
!define VERSIONMAJOR 1
!define VERSIONMINOR 0
!define VERSIONBUILD 0
!define HELPURL "https://github.com/yourusername/music-tagger"
!define UPDATEURL "https://github.com/yourusername/music-tagger"
!define ABOUTURL "https://github.com/yourusername/music-tagger"

!include "MUI2.nsh"
!include "FileFunc.nsh"

Name "${{APPNAME}}"
OutFile "dist\\MusicTagger-{version}-{timestamp}-setup.exe"
InstallDir "$PROGRAMFILES\\${{COMPANYNAME}}\\${{APPNAME}}"
InstallDirRegKey HKCU "Software\\${{COMPANYNAME}}\\${{APPNAME}}" ""

!define MUI_ABORTWARNING
!define MUI_ICON "dist\\MusicTagger\\MusicTagger.exe"
!define MUI_UNICON "dist\\MusicTagger\\MusicTagger.exe"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!define MUI_FINISHPAGE_RUN "$INSTDIR\\MusicTagger.exe"
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

Section "Install"
  SetOutPath "$INSTDIR"
  
  ; Recursively copy all files from the build directory
  File /r "dist\\MusicTagger\\*.*"
  
  ; Create uninstaller
  WriteUninstaller "$INSTDIR\\Uninstall.exe"
  
  ; Create start menu shortcut
  CreateDirectory "$SMPROGRAMS\\${{COMPANYNAME}}"
  CreateShortCut "$SMPROGRAMS\\${{COMPANYNAME}}\\${{APPNAME}}.lnk" "$INSTDIR\\MusicTagger.exe"
  
  ; Create desktop shortcut
  CreateShortCut "$DESKTOP\\${{APPNAME}}.lnk" "$INSTDIR\\MusicTagger.exe"
  
  ; Add to Add/Remove Programs
  WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{COMPANYNAME}} ${{APPNAME}}" "DisplayName" "${{APPNAME}}"
  WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{COMPANYNAME}} ${{APPNAME}}" "UninstallString" "$INSTDIR\\Uninstall.exe"
  WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{COMPANYNAME}} ${{APPNAME}}" "DisplayIcon" "$INSTDIR\\MusicTagger.exe"
  WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{COMPANYNAME}} ${{APPNAME}}" "Publisher" "${{COMPANYNAME}}"
  WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{COMPANYNAME}} ${{APPNAME}}" "URLInfoAbout" "${{ABOUTURL}}"
  WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{COMPANYNAME}} ${{APPNAME}}" "DisplayVersion" "{version}"
  
  ; Get size of the installation
  ${{GetSize}} "$INSTDIR" "/S=0K" $0 $1 $2
  IntFmt $0 "0x%08X" $0
  WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{COMPANYNAME}} ${{APPNAME}}" "EstimatedSize" "$0"
SectionEnd

Section "Uninstall"
  ; Remove files and uninstaller
  RMDir /r "$INSTDIR\\*.*"
  Delete "$INSTDIR\\Uninstall.exe"
  RMDir "$INSTDIR"
  
  ; Remove shortcuts
  Delete "$DESKTOP\\${{APPNAME}}.lnk"
  Delete "$SMPROGRAMS\\${{COMPANYNAME}}\\${{APPNAME}}.lnk"
  RMDir "$SMPROGRAMS\\${{COMPANYNAME}}"
  
  ; Remove registry keys
  DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{COMPANYNAME}} ${{APPNAME}}"
  DeleteRegKey HKCU "Software\\${{COMPANYNAME}}\\${{APPNAME}}"
SectionEnd
""")
    except Exception as e:
        print(f"Error creating NSIS script: {str(e)}")
        return False
    
    # Run NSIS
    success = run_command([
        nsis_path, 
        nsis_script
    ])
    
    if success:
        print("\nInstaller created successfully!")
        # Clean up
        if os.path.exists(nsis_script):
            os.remove(nsis_script)
        return True
    else:
        print("Failed to create installer")
        return False

def create_zip_package():
    """Create a ZIP package of the executable"""
    banner("Creating ZIP package")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(base_dir, "dist")
    app_dir = os.path.join(dist_dir, "MusicTagger")
    
    if not os.path.exists(app_dir):
        print(f"Application directory not found: {app_dir}")
        return False
    
    # Create zip filename with version and timestamp
    version = "1.0.0"  # You can get this dynamically if needed
    timestamp = datetime.datetime.now().strftime("%Y%m%d")
    zip_file = os.path.join(dist_dir, f"MusicTagger-{version}-{timestamp}.zip")
    
    try:
        import zipfile
        
        print(f"Creating ZIP file: {zip_file}")
        with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(app_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, dist_dir)
                    zipf.write(file_path, arcname)
        
        print("\nZIP package created successfully!")
        return True
    except Exception as e:
        print(f"Error creating ZIP package: {str(e)}")
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Build Music Tagger executable and installer")
    parser.add_argument("--exe-only", action="store_true", help="Build only the executable, not the installer")
    parser.add_argument("--installer-only", action="store_true", help="Build only the installer (requires executable to be built first)")
    parser.add_argument("--zip", action="store_true", help="Create a ZIP package of the executable")
    args = parser.parse_args()
    
    banner("Music Tagger Build Script")
    
    if not args.installer_only:
        # Build executable
        exe_success = build_executable()
        if not exe_success:
            print("Failed to build executable")
            return 1
    
    if platform.system() == "Windows" and not args.exe_only:
        # Create installer on Windows
        installer_success = create_installer()
        if not installer_success:
            print("Failed to create installer")
    
    if args.zip or platform.system() != "Windows":
        # Create ZIP package (always for non-Windows, optional for Windows)
        zip_success = create_zip_package()
        if not zip_success:
            print("Failed to create ZIP package")
    
    banner("Build completed successfully!")
    print(f"Output files can be found in the '{os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dist')}' directory")
    return 0

if __name__ == "__main__":
    sys.exit(main())
