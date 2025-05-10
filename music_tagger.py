import os
import sys
import time
import pathlib
import struct
import wave
import shutil
import configparser
from threading import Thread
from watchdog.observers.polling import PollingObserver as Observer  # More compatible observer
from watchdog.events import FileSystemEventHandler
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TPE1  # TPE1 is the artist tag
from mutagen.flac import FLAC
import tinytag

# Add user site-packages to sys.path if needed
user_site_packages = os.path.expanduser('~/.local/lib/python3/site-packages')
if os.path.exists(user_site_packages) and user_site_packages not in sys.path:
    sys.path.append(user_site_packages)

# Windows-specific paths - add all relevant Python paths
for path in [
    os.path.expanduser('~/AppData/Roaming/Python'),
    os.path.expanduser('~/AppData/Roaming/Python/Python313'),
    os.path.expanduser('~/AppData/Roaming/Python/Python313/site-packages')
]:
    if os.path.exists(path) and path not in sys.path:
        sys.path.append(path)
        print(f"Added to Python path: {path}")
        
# Also add to system PATH environment variable for subprocesses
roaming_python = os.path.expanduser('~/AppData/Roaming/Python')
if os.path.exists(roaming_python) and roaming_python not in os.environ.get('PATH', ''):
    os.environ['PATH'] = roaming_python + os.pathsep + os.environ.get('PATH', '')

# Attempt to import taglib, with fallback options
try:
    import taglib
    HAVE_TAGLIB = True
except ImportError:
    HAVE_TAGLIB = False
    print("Warning: taglib not available. WAV files will be tagged with companion files.")

class MusicFileHandler(FileSystemEventHandler):
    def __init__(self, artist_name):
        self.artist_name = artist_name
        self.processed_files = set()  # Keep track of processed files to avoid duplicates
        print(f"Watching for new music files... Artist: {artist_name}")

    def on_created(self, event):
        if not event.is_directory:
            file_path = event.src_path
            # Skip if we've already processed this file
            if file_path in self.processed_files:
                return
                
            # Check if it's an audio file
            if self.is_audio_file(file_path):
                relative_path = os.path.relpath(file_path, os.path.dirname(os.path.dirname(file_path)))
                print(f"New audio file detected: {relative_path}")
                try:
                    # Wait a bit to ensure file is fully written
                    time.sleep(1)
                    self.tag_music_file(file_path)
                    # Add to processed files set
                    self.processed_files.add(file_path)
                except Exception as e:
                    print(f"Error processing file {file_path}: {str(e)}")

    def is_audio_file(self, file_path):
        """Check if file is an audio file we support"""
        supported_extensions = ['.mp3', '.flac', '.wav', '.mid', '.midi']
        return any(file_path.lower().endswith(ext) for ext in supported_extensions)

    def tag_music_file(self, file_path):
        try:
            # Determine file type and create appropriate tag object
            if file_path.lower().endswith('.mp3'):
                audio = MP3(file_path, ID3=ID3)
                if audio.tags is None:
                    audio.add_tags()
                audio.tags.add(TPE1(encoding=3, text=self.artist_name))
                audio.save()
                print(f"Successfully tagged MP3 file {file_path} with artist: {self.artist_name}")
            elif file_path.lower().endswith('.flac'):
                audio = FLAC(file_path)
                if 'artist' not in audio.tags:
                    audio.tags['artist'] = [self.artist_name]
                audio.save()
                print(f"Successfully tagged FLAC file {file_path} with artist: {self.artist_name}")
            elif file_path.lower().endswith('.wav'):
                self.tag_wav_file(file_path)
            elif file_path.lower().endswith(('.mid', '.midi')):
                # MIDI files don't support tagging
                print(f"Note: {file_path} is a MIDI file and cannot be tagged directly")
            else:
                print(f"Unsupported file type: {file_path}")
                return
        except Exception as e:
            print(f"Error tagging file {file_path}: {str(e)}")
            
    def tag_wav_file(self, file_path):
        """Add artist metadata to WAV file"""
        if HAVE_TAGLIB:
            try:
                self.tag_wav_with_taglib(file_path)
            except Exception as e:
                print(f"Error tagging WAV file with taglib: {str(e)}")
                # Fall back to companion file method
                self.tag_wav_with_companion_file(file_path)
        else:
            # If taglib is not available, use companion file method
            self.tag_wav_with_companion_file(file_path)
            
    def tag_wav_with_taglib(self, file_path):
        """Tag WAV file directly using taglib"""
        try:
            # Create a backup of the original file first
            backup_path = file_path + ".backup"
            shutil.copy2(file_path, backup_path)
            
            # Open the file with taglib
            with taglib.File(file_path, save_on_exit=True) as audio:
                # Set the artist tag
                audio.tags["ARTIST"] = [self.artist_name]
                # Set additional metadata
                audio.tags["COMMENT"] = [f"Tagged by Music Tagger on {time.strftime('%Y-%m-%d %H:%M:%S')}"]                
            
            # Remove the backup if successful
            if os.path.exists(backup_path):
                os.remove(backup_path)
                
            print(f"Successfully embedded artist tag in WAV file: {file_path}")
            return True
            
        except Exception as e:
            # Restore from backup if available
            if os.path.exists(backup_path):
                shutil.copy2(backup_path, file_path)
                os.remove(backup_path)
                print(f"Restored original WAV file from backup after error")
            raise e
            
    def tag_wav_with_companion_file(self, file_path):
        """Tag WAV file using a companion metadata file"""
        try:
            # Create a text file with the same name
            metadata_path = file_path + ".artist.txt"
            
            # Write the metadata to the file
            with open(metadata_path, 'w', encoding='utf-8') as f:
                f.write(f"Artist: {self.artist_name}\n")
                f.write(f"Tagged by Music Tagger on {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            print(f"Successfully tagged WAV file {file_path} with artist: {self.artist_name}")
            print(f"Metadata saved to: {metadata_path}")
            return True
            
        except Exception as e:
            print(f"Error creating companion file for WAV: {str(e)}")
            return False

def load_config(config_path=None):
    """Load configuration from config.ini file"""
    if config_path is None:
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
    
    if not os.path.exists(config_path):
        print(f"Configuration file not found: {config_path}")
        return None
    
    try:
        config = configparser.ConfigParser()
        config.read(config_path)
        
        # Parse folder-artist mappings
        folder_mappings = {}
        if 'Folders' in config:
            for folder_path, artist_name in config['Folders'].items():
                # Clean up the paths (especially important for Windows paths)
                folder_path = folder_path.strip()
                artist_name = artist_name.strip()
                folder_mappings[folder_path] = artist_name
        
        # Get general settings
        settings = {}
        if 'MusicTagger' in config:
            for key, value in config['MusicTagger'].items():
                settings[key] = value.strip()
        
        return {
            'folder_mappings': folder_mappings,
            'settings': settings
        }
    except Exception as e:
        print(f"Error loading configuration: {str(e)}")
        return None

def create_folder_handler(folder_path, artist_name):
    """Create a handler for a specific folder"""
    # Check if folder exists
    if not os.path.exists(folder_path):
        try:
            os.makedirs(folder_path)
            print(f"Created folder: {folder_path}")
        except Exception as e:
            print(f"Error creating folder: {str(e)}")
            return None
    
    # Create event handler
    event_handler = MusicFileHandler(artist_name)
    return event_handler

def interactive_mode():
    """Run the application in interactive mode"""
    print("=== Music Tagger Interactive Mode ===")
    print("You can add multiple folders to watch, each with a different artist name.")
    print("Enter 'done' when finished adding folders.")
    
    folder_mappings = {}
    count = 1
    
    while True:
        print(f"\n--- Folder {count} ---")
        folder_path = input("Enter folder path to watch (or 'done' to finish): ")
        
        if folder_path.lower() == 'done':
            break
            
        artist_name = input("Enter artist name for this folder: ")
        folder_mappings[folder_path] = artist_name
        count += 1
    
    if not folder_mappings:
        print("No folders specified. Exiting.")
        return
        
    # Save the configuration
    config = configparser.ConfigParser()
    config['MusicTagger'] = {'log_level': 'INFO'}
    config['Folders'] = folder_mappings
    
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
    with open(config_path, 'w') as f:
        config.write(f)
        
    print(f"Configuration saved to {config_path}")
    print("Starting the application with the specified folders...")
    
    # Run with the newly created configuration
    config_mode()

def config_mode():
    """Run the application using configuration from config.ini"""
    config = load_config()
    if not config:
        print("Failed to load configuration. Use interactive mode or create a valid config.ini")
        return
        
    folder_mappings = config['folder_mappings']
    if not folder_mappings:
        print("No folder mappings found in the configuration.")
        return
        
    # Create observer - using PollingObserver for better compatibility
    observer = Observer()
    
    # Schedule handlers for each folder
    handlers = []
    for folder_path, artist_name in folder_mappings.items():
        handler = create_folder_handler(folder_path, artist_name)
        if handler:
            observer.schedule(handler, folder_path, recursive=True)  # Watch subdirectories too
            handlers.append(handler)
            print(f"Watching folder: {folder_path} for artist: {artist_name}")
    
    if not handlers:
        print("No valid folders to watch. Exiting.")
        return
        
    print("Press Ctrl+C to stop watching")

def main():
    # Check if config.ini exists
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
    if os.path.exists(config_path):
        # Ask user which mode to use
        print("Configuration file found. Choose operating mode:")
        print("1. Use existing configuration (config.ini)")
        print("2. Interactive mode (create new configuration)")
        choice = input("Enter your choice (1/2): ")
        
        if choice == '1':
            config_mode()
        else:
            interactive_mode()
    else:
        # No config, use interactive mode
        print("No configuration file found. Starting in interactive mode.")
        interactive_mode()
    
    # Run the observer in a safer way
    try:
        observer.start()
        try:
            while observer.is_alive():
                observer.join(1)
        except KeyboardInterrupt:
            pass
        finally:
            print("\nStopping watcher...")
            observer.stop()
            observer.join()
    except Exception as e:
        print(f"Observer error: {str(e)}")

if __name__ == "__main__":
    main()
