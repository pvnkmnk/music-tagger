#!/usr/bin/env python3
"""
Music Tagger Project Packager
Creates a ZIP file of the project for Google Colab build
"""
import os
import zipfile
import datetime

def create_project_zip():
    """Create a ZIP file of the project for Google Colab build"""
    # Get the project directory (where this script is located)
    project_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define the output ZIP file name with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = os.path.join(project_dir, f"music_tagger_colab_{timestamp}.zip")
    
    # Files to include in the ZIP
    required_files = [
        'music_tagger_mobile.py',  # Main mobile app file
        'music_tagger.py',         # Core functionality
        'buildozer.spec',          # Buildozer configuration
        'config.ini.sample',       # Sample configuration
        'README.md',               # Documentation
        'requirements_mobile.txt', # Mobile requirements
    ]
    
    # Optional files to include if they exist
    optional_files = [
        'assets',                 # Any assets directory
        'images',                 # Any images directory
        'LICENSE',                # License file
    ]
    
    # Create the ZIP file
    print(f"Creating ZIP file: {zip_filename}")
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add required files
        for file in required_files:
            filepath = os.path.join(project_dir, file)
            if os.path.exists(filepath):
                print(f"Adding: {file}")
                if os.path.isdir(filepath):
                    # For directories, add all files recursively
                    for root, _, files in os.walk(filepath):
                        for f in files:
                            full_path = os.path.join(root, f)
                            relative_path = os.path.relpath(full_path, project_dir)
                            zipf.write(full_path, relative_path)
                else:
                    # For single files
                    zipf.write(filepath, file)
            else:
                print(f"Warning: Required file not found: {file}")
        
        # Add optional files if they exist
        for file in optional_files:
            filepath = os.path.join(project_dir, file)
            if os.path.exists(filepath):
                print(f"Adding optional: {file}")
                if os.path.isdir(filepath):
                    # For directories, add all files recursively
                    for root, _, files in os.walk(filepath):
                        for f in files:
                            full_path = os.path.join(root, f)
                            relative_path = os.path.relpath(full_path, project_dir)
                            zipf.write(full_path, relative_path)
                else:
                    # For single files
                    zipf.write(filepath, file)
    
    print(f"\nZIP file created successfully: {zip_filename}")
    print("\nInstructions:")
    print("1. Upload the build_android_app.ipynb notebook to Google Colab")
    print("2. Upload this ZIP file when prompted in the notebook")
    print("3. Follow the steps in the notebook to build your Android APK")
    
    return zip_filename

if __name__ == "__main__":
    create_project_zip()
