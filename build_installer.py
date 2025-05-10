#!/usr/bin/env python3
"""
Script to build the Music Tagger installer
"""
import os
import sys
import subprocess
import platform
import datetime
from PIL import Image, ImageDraw, ImageFont

def create_installer_graphics():
    """Create installer graphics if they don't exist"""
    assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "installer_assets")
    
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir, exist_ok=True)
    
    # Create welcome banner (164x314 pixels)
    welcome_path = os.path.join(assets_dir, "welcome.bmp")
    if not os.path.exists(welcome_path):
        try:
            img = Image.new('RGB', (164, 314), (0, 120, 120))
            draw = ImageDraw.Draw(img)
            
            # Add text
            try:
                font = ImageFont.truetype("arial.ttf", 14)
            except:
                font = ImageFont.load_default()
                
            draw.text((20, 100), "Music Tagger", fill=(255, 255, 255), font=font)
            draw.text((20, 120), "Version 1.0.0", fill=(255, 255, 255), font=font)
            draw.text((20, 160), "Auto-tag your", fill=(255, 255, 255), font=font)
            draw.text((20, 180), "music files", fill=(255, 255, 255), font=font)
            
            img.save(welcome_path)
            print(f"Created welcome image: {welcome_path}")
        except Exception as e:
            print(f"Error creating welcome image: {str(e)}")
    
    # Create header banner (150x57 pixels)
    header_path = os.path.join(assets_dir, "header.bmp")
    if not os.path.exists(header_path):
        try:
            img = Image.new('RGB', (150, 57), (0, 120, 120))
            draw = ImageDraw.Draw(img)
            
            # Add text
            try:
                font = ImageFont.truetype("arial.ttf", 12)
            except:
                font = ImageFont.load_default()
                
            draw.text((10, 20), "Music Tagger", fill=(255, 255, 255), font=font)
            
            img.save(header_path)
            print(f"Created header image: {header_path}")
        except Exception as e:
            print(f"Error creating header image: {str(e)}")

def find_nsis():
    """Find the NSIS executable path"""
    # Try common paths
    nsis_paths = [
        r"C:\Program Files (x86)\NSIS\makensis.exe",
        r"C:\Program Files\NSIS\makensis.exe"
    ]
    
    for path in nsis_paths:
        if os.path.exists(path):
            return path
    
    # Try to find via command line
    try:
        result = subprocess.run(["where", "makensis"], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    
    return None

def build_installer():
    """Build the installer using NSIS"""
    # Find NSIS
    nsis_path = find_nsis()
    if not nsis_path:
        print("NSIS not found. Please install it from: https://nsis.sourceforge.io/Download")
        print("Would you like to continue with ZIP packaging instead? (y/n)")
        choice = input().lower()
        if choice != 'y':
            return False
        return create_zip_package()
    
    # Run NSIS
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "installer.nsi")
    
    print(f"Building installer using NSIS: {nsis_path}")
    print(f"Script: {script_path}")
    
    try:
        process = subprocess.Popen(
            [nsis_path, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        
        # Print output in real-time
        for line in process.stdout:
            print(line.strip())
        
        process.wait()
        
        if process.returncode == 0:
            installer_name = f"MusicTagger-1.0.0-Setup.exe"
            installer_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), installer_name)
            
            if os.path.exists(installer_path):
                print(f"\nInstaller created successfully: {installer_path}")
                return True
            else:
                print("\nNSIS completed successfully, but installer file not found")
                return False
        else:
            print(f"\nError building installer: NSIS returned code {process.returncode}")
            return False
    except Exception as e:
        print(f"Error running NSIS: {str(e)}")
        return False

def create_zip_package():
    """Create a ZIP package of the executable as a fallback"""
    import zipfile
    from datetime import datetime
    
    print("Creating ZIP package instead...")
    
    # Get the project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(project_dir, "dist", "MusicTagger")
    
    if not os.path.exists(dist_dir):
        print(f"Error: Distribution directory not found: {dist_dir}")
        return False
    
    # Create ZIP file name with timestamp
    timestamp = datetime.now().strftime("%Y%m%d")
    zip_filename = os.path.join(project_dir, f"MusicTagger-1.0.0-{timestamp}.zip")
    
    try:
        # Create the ZIP file
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add all files from the distribution directory
            for root, _, files in os.walk(dist_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Calculate the relative path
                    rel_path = os.path.relpath(file_path, dist_dir)
                    zipf.write(file_path, rel_path)
        
        print(f"ZIP package created: {zip_filename}")
        return True
    except Exception as e:
        print(f"Error creating ZIP package: {str(e)}")
        return False

def create_readme():
    """Create a README.md file if it doesn't exist"""
    project_dir = os.path.dirname(os.path.abspath(__file__))
    readme_path = os.path.join(project_dir, "README.md")
    
    if not os.path.exists(readme_path):
        with open(readme_path, 'w') as f:
            f.write("# Music Tagger\n\n")
            f.write("A modern application for automatic music file tagging with Material Design UI.\n\n")
            
            f.write("## Features\n\n")
            f.write("- Automatically tag music files based on folder structure\n")
            f.write("- Monitor multiple folders with different artist names\n")
            f.write("- Support for MP3, FLAC, WAV, and MIDI files\n")
            f.write("- Material Design UI with dark mode support\n")
            f.write("- System tray integration for background monitoring\n")
            f.write("- Full configuration through user-friendly interface\n\n")
            
            f.write("## Installation\n\n")
            f.write("### Windows Installer\n\n")
            f.write("1. Download the latest installer from the [Releases](https://github.com/yourusername/music-tagger/releases) page\n")
            f.write("2. Run the installer and follow the on-screen instructions\n")
            f.write("3. Launch Music Tagger from the Start menu\n\n")
            
            f.write("### Manual Installation\n\n")
            f.write("1. Clone this repository\n")
            f.write("2. Install the required dependencies:\n   ```\n   pip install -r requirements.txt\n   ```\n")
            f.write("3. Run the application:\n   ```\n   python music_tagger_gui.py\n   ```\n\n")
            
            f.write("## Configuration\n\n")
            f.write("1. Launch Music Tagger\n")
            f.write("2. Add folders to monitor by clicking the 'Add Folder' button\n")
            f.write("3. Specify the artist name for each folder\n")
            f.write("4. Click 'Start Monitoring' to begin automatic tagging\n\n")
            
            f.write("## Building from Source\n\n")
            f.write("To build the standalone executable:\n\n")
            f.write("```\npython build_debug.py\n```\n\n")
            f.write("The executable will be created in the `dist/MusicTagger` directory.\n\n")
            
            f.write("## License\n\n")
            f.write("This project is licensed under the MIT License - see the LICENSE file for details.\n")
        
        print(f"Created README.md file: {readme_path}")
    else:
        print(f"README.md already exists: {readme_path}")
    
    return True

def prepare_for_github():
    """Prepare the project for GitHub publication"""
    # Get the project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create .gitignore if it doesn't exist
    gitignore_path = os.path.join(project_dir, ".gitignore")
    if not os.path.exists(gitignore_path):
        with open(gitignore_path, 'w') as f:
            f.write("# Python\n")
            f.write("__pycache__/\n")
            f.write("*.py[cod]\n")
            f.write("*$py.class\n")
            f.write("*.so\n")
            f.write(".Python\n")
            f.write("build/\n")
            f.write("develop-eggs/\n")
            f.write("dist/\n")
            f.write("downloads/\n")
            f.write("eggs/\n")
            f.write(".eggs/\n")
            f.write("lib/\n")
            f.write("lib64/\n")
            f.write("parts/\n")
            f.write("sdist/\n")
            f.write("var/\n")
            f.write("wheels/\n")
            f.write("*.egg-info/\n")
            f.write(".installed.cfg\n")
            f.write("*.egg\n")
            f.write("\n")
            f.write("# Installer logs\n")
            f.write("pip-log.txt\n")
            f.write("pip-delete-this-directory.txt\n")
            f.write("\n")
            f.write("# Unit test / coverage reports\n")
            f.write("htmlcov/\n")
            f.write(".tox/\n")
            f.write(".coverage\n")
            f.write(".coverage.*\n")
            f.write(".cache\n")
            f.write("nosetests.xml\n")
            f.write("coverage.xml\n")
            f.write("*.cover\n")
            f.write(".hypothesis/\n")
            f.write("\n")
            f.write("# Environments\n")
            f.write(".env\n")
            f.write(".venv\n")
            f.write("env/\n")
            f.write("venv/\n")
            f.write("ENV/\n")
            f.write("env.bak/\n")
            f.write("venv.bak/\n")
            f.write("\n")
            f.write("# VSCode\n")
            f.write(".vscode/\n")
            f.write("\n")
            f.write("# PyCharm\n")
            f.write(".idea/\n")
            f.write("\n")
            f.write("# Application specific\n")
            f.write("*.log\n")
            f.write("config.ini\n")
            f.write("\n")
            f.write("# Installers\n")
            f.write("*.exe\n")
            f.write("!dist/*.exe\n")
            f.write("\n")
        
        print(f"Created .gitignore file: {gitignore_path}")
    else:
        print(f".gitignore already exists: {gitignore_path}")
    
    # Create a simple LICENSE file if it doesn't exist
    license_path = os.path.join(project_dir, "LICENSE")
    if not os.path.exists(license_path):
        with open(license_path, 'w') as f:
            f.write("MIT License\n\n")
            f.write(f"Copyright (c) {datetime.datetime.now().year} MusicTagger Contributors\n\n")
            f.write("Permission is hereby granted, free of charge, to any person obtaining a copy\n")
            f.write("of this software and associated documentation files (the \"Software\"), to deal\n")
            f.write("in the Software without restriction, including without limitation the rights\n")
            f.write("to use, copy, modify, merge, publish, distribute, sublicense, and/or sell\n")
            f.write("copies of the Software, and to permit persons to whom the Software is\n")
            f.write("furnished to do so, subject to the following conditions:\n\n")
            f.write("The above copyright notice and this permission notice shall be included in all\n")
            f.write("copies or substantial portions of the Software.\n\n")
            f.write("THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\n")
            f.write("IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\n")
            f.write("FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\n")
            f.write("AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\n")
            f.write("LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\n")
            f.write("OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE\n")
            f.write("SOFTWARE.\n")
        print(f"Created LICENSE file: {license_path}")
    else:
        print(f"LICENSE file already exists: {license_path}")
    
    return True

def main():
    print("=== Music Tagger Package Builder ===")
    
    # Create ZIP package directly (skip NSIS due to errors)
    print("\nCreating ZIP package...")
    success = create_zip_package()
    
    # Prepare for GitHub regardless of ZIP success
    print("\nPreparing for GitHub publication...")
    prepare_for_github()
    
    # Create a README.md file if it doesn't exist
    create_readme()
    
    print("\n===== All Done! =====")
    print("\nNext steps for GitHub publication:")
    print("1. Create a new GitHub repository at https://github.com/new")
    print("2. Initialize the local git repository:")
    print("   git init")
    print("   git add .")
    print("   git commit -m \"Initial commit\"")
    print("3. Connect and push to your GitHub repository:")
    print("   git remote add origin https://github.com/yourusername/music-tagger.git")
    print("   git push -u origin master")
    print("\n4. Upload the ZIP package as a GitHub Release:")
    print("   - Go to your GitHub repository")
    print("   - Click on 'Releases' -> 'Create a new release'")
    print("   - Set the tag version to v1.0.0")
    print("   - Upload your ZIP package")
    print("   - Publish the release")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
