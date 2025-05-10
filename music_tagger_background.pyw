import os
import sys
import time
import logging
import configparser
from watchdog.observers.polling import PollingObserver
from music_tagger import MusicFileHandler

# Configure logging
log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'music_tagger_background.log')
logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def load_config():
    """Load configuration from the config file"""
    try:
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
        
        # Check if config file exists
        if not os.path.exists(config_path):
            logging.error(f"Configuration file not found: {config_path}")
            return None
            
        # Read configuration
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
        else:
            logging.error("Invalid configuration file: missing [Folders] section")
            return None
            
        if not folder_mappings:
            logging.error("No folder mappings found in configuration")
            return None
        
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
        logging.error(f"Error loading configuration: {str(e)}")
        return None

def create_folder_handler(folder_path, artist_name):
    """Create and configure a handler for a folder"""
    # Check if folder exists
    if not os.path.exists(folder_path):
        try:
            os.makedirs(folder_path)
            logging.info(f"Created folder: {folder_path}")
        except Exception as e:
            logging.error(f"Error creating folder '{folder_path}': {str(e)}")
            return None
    
    # Create and return event handler
    return MusicFileHandler(artist_name)

def main():
    try:
        # Add user-specific Python paths to system path
        user_python_path = os.path.expanduser('~/AppData/Roaming/Python')
        if os.path.exists(user_python_path):
            os.environ['PATH'] = user_python_path + os.pathsep + os.environ.get('PATH', '')
            
        # Load configuration
        config = load_config()
        if not config:
            logging.error("Failed to load configuration. Application will exit.")
            return
            
        folder_mappings = config.get('folder_mappings', {})
        settings = config.get('settings', {})
        
        if not folder_mappings:
            logging.error("No folder mappings found. Application will exit.")
            return
            
        # Set log level from settings
        if 'log_level' in settings:
            numeric_level = getattr(logging, settings['log_level'].upper(), None)
            if isinstance(numeric_level, int):
                logging.getLogger().setLevel(numeric_level)
            
        logging.info(f"Starting Music Tagger Background Monitor")
        logging.info(f"Monitoring {len(folder_mappings)} folders")
        
        # Create observer
        observer = PollingObserver()
        
        # Set up handlers for each folder
        handlers = []
        for folder_path, artist_name in folder_mappings.items():
            logging.info(f"Setting up monitoring for folder: {folder_path} with artist: {artist_name}")
            handler = create_folder_handler(folder_path, artist_name)
            if handler:
                observer.schedule(handler, folder_path, recursive=True)
                handlers.append(handler)
                logging.info(f"Successfully configured monitoring for {folder_path}")
            else:
                logging.error(f"Failed to configure monitoring for {folder_path}")
        
        if not handlers:
            logging.error("No valid folders to monitor. Application will exit.")
            return
            
        observer.start()
        logging.info(f"Observer started monitoring {len(handlers)} folders")
        
        # Keep running until manually terminated
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            logging.info("Keyboard interrupt received. Stopping observer.")
        
        observer.join()
        logging.info("Observer joined. Application exiting.")
        
    except Exception as e:
        logging.error(f"Application error: {str(e)}")

if __name__ == "__main__":
    main()
