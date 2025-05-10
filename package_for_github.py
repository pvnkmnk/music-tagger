#!/usr/bin/env python3
"""
Simple script to create a release package and prepare for GitHub
"""
import os
import sys
import zipfile
import datetime
import shutil

def create_zip_package():
    """Create a simple ZIP package of the executable"""
    print("Creating ZIP package...")
    
    # Get the project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(project_dir, "dist", "MusicTagger")
    
    if not os.path.exists(dist_dir):
        print(f"Error: Distribution directory not found: {dist_dir}")
        print("Please run build_debug.py first to create the executable.")
        return False
    
    # Create ZIP file name with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d")
    zip_filename = os.path.join(project_dir, f"MusicTagger-1.0.0-{timestamp}.zip")
    
    # Remove existing ZIP if it exists
    if os.path.exists(zip_filename):
        try:
            os.remove(zip_filename)
            print(f"Removed existing ZIP: {zip_filename}")
        except Exception as e:
            print(f"Warning: Could not remove existing ZIP: {e}")
    
    try:
        # Create the ZIP file
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add all files from the distribution directory
            file_count = 0
            for root, _, files in os.walk(dist_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Calculate the relative path
                    rel_path = os.path.relpath(file_path, dist_dir)
                    zipf.write(file_path, rel_path)
                    file_count += 1
            
            # Add README and LICENSE
            for extra_file in ["README.md", "LICENSE"]:
                extra_path = os.path.join(project_dir, extra_file)
                if os.path.exists(extra_path):
                    zipf.write(extra_path, extra_file)
                    file_count += 1
        
        print(f"ZIP package created with {file_count} files: {zip_filename}")
        return True
    except Exception as e:
        print(f"Error creating ZIP package: {e}")
        return False

def ensure_readme_exists():
    """Make sure README.md exists with basic content"""
    project_dir = os.path.dirname(os.path.abspath(__file__))
    readme_path = os.path.join(project_dir, "README.md")
    
    if not os.path.exists(readme_path):
        print("Creating README.md...")
        with open(readme_path, 'w') as f:
            f.write("# Music Tagger\n\n")
            f.write("A modern application for automatic music file tagging with Material Design UI.\n\n")
            f.write("## Features\n\n")
            f.write("- Automatically tag music files based on folder structure\n")
            f.write("- Monitor multiple folders with different artist names\n")
            f.write("- Support for MP3, FLAC, WAV, and MIDI files\n")
            f.write("- Material Design UI with dark mode support\n")
            f.write("- System tray integration for background monitoring\n\n")
            
            f.write("## Installation\n\n")
            f.write("Download the latest release ZIP from the [Releases](https://github.com/yourusername/music-tagger/releases) page.\n\n")
            
            f.write("## Usage\n\n")
            f.write("1. Extract the ZIP file\n")
            f.write("2. Run MusicTagger.exe\n")
            f.write("3. Add folders to monitor and specify artist names\n")
            f.write("4. Start monitoring\n\n")
            
            f.write("## License\n\n")
            f.write("This project is licensed under the MIT License - see the LICENSE file for details.\n")
        
        print(f"Created README.md: {readme_path}")
    else:
        print(f"README.md already exists: {readme_path}")

def ensure_gitignore_exists():
    """Make sure .gitignore exists with necessary exclusions"""
    project_dir = os.path.dirname(os.path.abspath(__file__))
    gitignore_path = os.path.join(project_dir, ".gitignore")
    
    if not os.path.exists(gitignore_path):
        print("Creating .gitignore...")
        with open(gitignore_path, 'w') as f:
            f.write("# Python\n")
            f.write("__pycache__/\n")
            f.write("*.py[cod]\n")
            f.write("build/\n")
            f.write("dist/\n")
            f.write("*.egg-info/\n\n")
            
            f.write("# Application specific\n")
            f.write("*.log\n")
            f.write("config.ini\n\n")
            
            f.write("# Release packages\n")
            f.write("*.zip\n")
            f.write("*.exe\n")
        
        print(f"Created .gitignore: {gitignore_path}")
    else:
        print(f".gitignore already exists: {gitignore_path}")

def main():
    print("=== Music Tagger Release Packager ===\n")
    
    # Make sure we have essential files
    ensure_readme_exists()
    ensure_gitignore_exists()
    
    # Create ZIP package
    if create_zip_package():
        print("\nPackage created successfully!")
        
        print("\nGitHub Publication Steps:")
        print("1. Visit: https://github.com/new")
        print("2. Repository name: music-tagger")
        print("3. Add description: 'Modern music file tagger with Material Design UI'")
        print("4. Make it Public")
        print("5. Click 'Create repository'")
        print("\nThen run these commands in your terminal:")
        print("git add .")
        print("git commit -m \"Initial release\"")
        print("git remote add origin https://github.com/yourusername/music-tagger.git")
        print("git push -u origin master")
        print("\nFinally, create a GitHub Release with your ZIP file")
    else:
        print("\nPackage creation failed.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
