import os
import sys
import time
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import logging
import configparser
import pathlib

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
        
# Also add to system PATH environment variable for subprocesses
roaming_python = os.path.expanduser('~/AppData/Roaming/Python')
if os.path.exists(roaming_python) and roaming_python not in os.environ.get('PATH', ''):
    os.environ['PATH'] = roaming_python + os.pathsep + os.environ.get('PATH', '')

from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler
from music_tagger import MusicFileHandler

# Configure logging
log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'music_tagger_service.log')
logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class MusicTaggerService(win32serviceutil.ServiceFramework):
    _svc_name_ = "MusicTaggerService"
    _svc_display_name_ = "Music Tagger Service"
    _svc_description_ = "Monitors specified folders for new music files and tags them with artist information"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)
        self.is_running = False
        self.observer = None
        
    def SvcStop(self):
        self.is_running = False
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        
        # Stop the observer if it's running
        if self.observer and self.observer.is_alive():
            self.observer.stop()
            self.observer.join(timeout=5)
            logging.info("Stopped directory observer")
        
        logging.info("Service stopping...")
        
    def SvcDoRun(self):
        self.is_running = True
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        
        logging.info("Service starting...")
        self.main()
        
    def main(self):
        try:
            # Load configuration
            config = self.load_config()
            if not config:
                logging.error("Failed to load configuration. Service will exit.")
                return
                
            folder_path = config.get('folder_path')
            artist_name = config.get('artist_name')
            
            if not folder_path or not artist_name:
                logging.error("Missing required configuration values. Service will exit.")
                return
                
            logging.info(f"Watching folder: {folder_path} for artist: {artist_name}")
            
            # Create event handler
            event_handler = MusicFileHandler(artist_name)
            
            # Create observer
            self.observer = PollingObserver()
            self.observer.schedule(event_handler, folder_path, recursive=True)
            self.observer.start()
            logging.info(f"Observer started watching folder: {folder_path}")
            
            # Run the service until it's stopped
            while self.is_running:
                # Check for stop event
                if win32event.WaitForSingleObject(self.hWaitStop, 1000) == win32event.WAIT_OBJECT_0:
                    break
                    
            # Stop the observer
            if self.observer.is_alive():
                self.observer.stop()
                self.observer.join()
                
        except Exception as e:
            logging.error(f"Service error: {str(e)}")
            
    def load_config(self):
        """Load configuration from the config file"""
        try:
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
            
            # Check if config file exists, create default if not
            if not os.path.exists(config_path):
                self.create_default_config(config_path)
                logging.warning(f"Created default configuration file at {config_path}")
                logging.warning("Please edit this file with your settings and restart the service")
                return None
                
            # Read configuration
            config = configparser.ConfigParser()
            config.read(config_path)
            
            if 'MusicTagger' not in config:
                logging.error("Invalid configuration file: missing [MusicTagger] section")
                return None
                
            required_keys = ['folder_path', 'artist_name']
            for key in required_keys:
                if key not in config['MusicTagger']:
                    logging.error(f"Invalid configuration file: missing '{key}' value")
                    return None
                    
            return {
                'folder_path': config['MusicTagger']['folder_path'],
                'artist_name': config['MusicTagger']['artist_name']
            }
            
        except Exception as e:
            logging.error(f"Error loading configuration: {str(e)}")
            return None
            
    def create_default_config(self, config_path):
        """Create a default configuration file"""
        try:
            config = configparser.ConfigParser()
            config['MusicTagger'] = {
                'folder_path': 'C:\\Music',
                'artist_name': 'Your Artist Name'
            }
            
            with open(config_path, 'w') as f:
                config.write(f)
                
        except Exception as e:
            logging.error(f"Error creating default configuration: {str(e)}")


if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(MusicTaggerService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(MusicTaggerService)
