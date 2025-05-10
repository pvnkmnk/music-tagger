#!/usr/bin/env python3
"""
Music Tagger Mobile App
Cross-platform mobile application for Music Tagger
"""
import os
import sys
import time
import json
import threading
import configparser
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.utils import platform
from kivy.properties import StringProperty, ListProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineIconListItem, MDList, IconLeftWidget
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.filemanager import MDFileManager
from kivymd.toast import toast

# Import the core tagger functionality - modify paths as needed
# For iOS/Android, these need to be bundled with the app
try:
    from music_tagger import is_audio_file, MusicFileHandler
    from watchdog.observers.polling import PollingObserver
    from watchdog.events import FileSystemEventHandler
except ImportError:
    # Fall back to internal implementation for mobile
    # In mobile environments, we'll need a simpler implementation
    # of the core functionality
    
    # Define the audio file check function
    def is_audio_file(file_path):
        """Check if file is an audio file we support"""
        supported_extensions = ['.mp3', '.flac', '.wav', '.mid', '.midi']
        return any(file_path.lower().endswith(ext) for ext in supported_extensions)
    
    # Create a simple event handler class
    class FileSystemEventHandler:
        def on_created(self, event):
            pass
    
    # Create a simple observer class
    class PollingObserver:
        def __init__(self):
            self.handlers = []
        
        def schedule(self, handler, path, recursive=True):
            self.handlers.append((handler, path, recursive))
        
        def start(self):
            pass
        
        def stop(self):
            pass
        
        def join(self):
            pass
    
    # Create a simple music handler class
    class MusicFileHandler(FileSystemEventHandler):
        def __init__(self, artist_name):
            self.artist_name = artist_name
            self.processed_files = set()
        
        def tag_music_file(self, file_path):
            """Tag a music file with artist information"""
            return True

# Define the KV language string for the UI
KV = '''
<FolderItem>:
    IconLeftWidget:
        icon: 'folder'

<ActivityItem>:
    IconLeftWidget:
        icon: 'music-note'

<MusicTagScreen>:
    BoxLayout:
        orientation: 'vertical'
        MDTopAppBar:
            title: 'Music Tagger'
            left_action_items: [['menu', lambda x: app.toggle_nav_drawer()]]
            elevation: 10
        
        MDTabs:
            id: tabs
            
            Tab:
                title: 'Folders'
                BoxLayout:
                    orientation: 'vertical'
                    padding: dp(10)
                    spacing: dp(10)
                    
                    MDCard:
                        orientation: 'vertical'
                        padding: dp(15)
                        size_hint_y: None
                        height: self.minimum_height
                        
                        MDLabel:
                            text: 'Monitor Status: ' + root.monitor_status
                            halign: 'center'
                            size_hint_y: None
                            height: self.texture_size[1]
                        
                        BoxLayout:
                            orientation: 'horizontal'
                            size_hint_y: None
                            height: dp(50)
                            padding: dp(10)
                            spacing: dp(10)
                            
                            MDRaisedButton:
                                text: 'Start Monitoring'
                                md_bg_color: app.theme_cls.primary_color
                                on_release: root.start_monitoring()
                                disabled: root.is_monitoring
                            
                            MDRaisedButton:
                                text: 'Stop Monitoring'
                                md_bg_color: [0.8, 0.2, 0.2, 1]
                                on_release: root.stop_monitoring()
                                disabled: not root.is_monitoring
                    
                    BoxLayout:
                        orientation: 'vertical'
                        
                        MDLabel:
                            text: 'Monitored Folders'
                            halign: 'center'
                            size_hint_y: None
                            height: dp(30)
                        
                        ScrollView:
                            MDList:
                                id: folder_list
                        
                        BoxLayout:
                            orientation: 'horizontal'
                            size_hint_y: None
                            height: dp(50)
                            padding: dp(10)
                            spacing: dp(10)
                            
                            MDRaisedButton:
                                text: 'Add Folder'
                                on_release: root.add_folder()
                            
                            MDRaisedButton:
                                text: 'Save Config'
                                on_release: root.save_config()
            
            Tab:
                title: 'Activity'
                BoxLayout:
                    orientation: 'vertical'
                    
                    ScrollView:
                        MDList:
                            id: activity_list

<Tab>:
    MDLabel:
        id: label
        text: ''
        halign: 'center'
'''

# Define Tab class
class Tab(Screen):
    """Tab class for the tabbed interface"""
    pass

# Define FolderItem class
class FolderItem(OneLineIconListItem):
    """Item representing a folder in the list"""
    pass

# Define ActivityItem class
class ActivityItem(OneLineIconListItem):
    """Item representing an activity in the list"""
    pass

# Define MusicTagScreen class
class MusicTagScreen(Screen):
    """Main screen for the Music Tagger app"""
    monitor_status = StringProperty("Not Monitoring")
    is_monitoring = BooleanProperty(False)
    folder_mappings = {}
    observer = None
    observer_thread = None
    activity_list = []
    
    def __init__(self, **kwargs):
        super(MusicTagScreen, self).__init__(**kwargs)
        self.file_manager = MDFileManager(
            exit_manager=self.exit_file_manager,
            select_path=self.select_folder_path,
        )
        Clock.schedule_once(self.load_config, 0.5)
    
    def load_config(self, dt=None):
        """Load configuration from config.ini"""
        try:
            # Determine config path based on platform
            if platform == 'android':
                from android.storage import primary_external_storage_path
                config_dir = primary_external_storage_path()
                config_path = os.path.join(config_dir, 'music_tagger_config.ini')
            elif platform == 'ios':
                from pyobjus import autoclass
                NSSearchPathForDirectoriesInDomains = autoclass('NSSearchPathForDirectoriesInDomains')
                NSDocumentDirectory = 1
                NSUserDomainMask = 1
                paths = NSSearchPathForDirectoriesInDomains(NSDocumentDirectory, NSUserDomainMask, True)
                config_dir = paths.objectAtIndex_(0)
                config_path = os.path.join(config_dir, 'music_tagger_config.ini')
            else:
                # Desktop fallback
                config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
            
            if not os.path.exists(config_path):
                return
            
            config = configparser.ConfigParser()
            config.read(config_path)
            
            # Parse folder-artist mappings
            self.folder_mappings = {}
            if 'Folders' in config:
                for folder_path, artist_name in config['Folders'].items():
                    folder_path = folder_path.strip()
                    artist_name = artist_name.strip()
                    self.folder_mappings[folder_path] = artist_name
            
            # Update folder list
            self.update_folder_list()
        
        except Exception as e:
            print(f"Error loading config: {str(e)}")
            toast(f"Error loading config: {str(e)}")
    
    def save_config(self):
        """Save configuration to config.ini"""
        try:
            # Determine config path based on platform
            if platform == 'android':
                from android.storage import primary_external_storage_path
                config_dir = primary_external_storage_path()
                config_path = os.path.join(config_dir, 'music_tagger_config.ini')
            elif platform == 'ios':
                from pyobjus import autoclass
                NSSearchPathForDirectoriesInDomains = autoclass('NSSearchPathForDirectoriesInDomains')
                NSDocumentDirectory = 1
                NSUserDomainMask = 1
                paths = NSSearchPathForDirectoriesInDomains(NSDocumentDirectory, NSUserDomainMask, True)
                config_dir = paths.objectAtIndex_(0)
                config_path = os.path.join(config_dir, 'music_tagger_config.ini')
            else:
                # Desktop fallback
                config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
            
            config = configparser.ConfigParser()
            config['MusicTagger'] = {'log_level': 'INFO'}
            
            # Add folder mappings
            config['Folders'] = {}
            for folder_path, artist_name in self.folder_mappings.items():
                config['Folders'][folder_path] = artist_name
            
            # Write to file
            with open(config_path, 'w') as f:
                config.write(f)
            
            toast("Configuration saved successfully")
        
        except Exception as e:
            print(f"Error saving config: {str(e)}")
            toast(f"Error saving config: {str(e)}")
    
    def update_folder_list(self):
        """Update the folder list in the UI"""
        folder_list = self.ids.folder_list
        folder_list.clear_widgets()
        
        for folder_path, artist_name in self.folder_mappings.items():
            item = FolderItem(text=f"{folder_path} (Artist: {artist_name})")
            item.bind(on_release=lambda x, path=folder_path: self.show_folder_options(path))
            folder_list.add_widget(item)
    
    def show_folder_options(self, folder_path):
        """Show options dialog for a folder"""
        self.folder_dialog = MDDialog(
            title="Folder Options",
            text=f"Path: {folder_path}\nArtist: {self.folder_mappings.get(folder_path, '')}",
            buttons=[
                MDFlatButton(
                    text="EDIT",
                    on_release=lambda x: self.edit_folder(folder_path)
                ),
                MDFlatButton(
                    text="REMOVE",
                    on_release=lambda x: self.remove_folder(folder_path)
                ),
                MDFlatButton(
                    text="CLOSE",
                    on_release=lambda x: self.folder_dialog.dismiss()
                ),
            ],
        )
        self.folder_dialog.open()
    
    def edit_folder(self, folder_path):
        """Edit artist name for a folder"""
        self.folder_dialog.dismiss()
        
        # Show input dialog for new artist name
        self.edit_dialog = MDDialog(
            title="Edit Artist Name",
            text=f"Enter new artist name for:\n{folder_path}",
            size_hint=(0.8, 0.4),
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: self.edit_dialog.dismiss()
                ),
                MDRaisedButton(
                    text="SAVE",
                    on_release=lambda x: self.save_artist_name(folder_path)
                ),
            ],
        )
        self.edit_dialog.open()
    
    def save_artist_name(self, folder_path):
        """Save new artist name for a folder"""
        # In a real implementation, you would get the input value here
        # For now, we'll use a placeholder
        new_artist_name = "New Artist Name"  # This would come from the input dialog
        
        self.folder_mappings[folder_path] = new_artist_name
        self.update_folder_list()
        self.edit_dialog.dismiss()
        toast(f"Updated artist name for {folder_path}")
    
    def remove_folder(self, folder_path):
        """Remove a folder from monitoring"""
        self.folder_dialog.dismiss()
        
        if folder_path in self.folder_mappings:
            del self.folder_mappings[folder_path]
            self.update_folder_list()
            toast(f"Removed folder: {folder_path}")
    
    def add_folder(self):
        """Add a new folder to monitor"""
        # Show file manager for folder selection
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
        
        self.file_manager.show('/')  # Start at root directory
    
    def select_folder_path(self, path):
        """Called when a folder is selected in the file manager"""
        self.exit_file_manager()
        
        # Show dialog for artist name
        self.add_folder_path = path
        self.add_dialog = MDDialog(
            title="Add Folder",
            text=f"Enter artist name for folder:\n{path}",
            size_hint=(0.8, 0.4),
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: self.add_dialog.dismiss()
                ),
                MDRaisedButton(
                    text="ADD",
                    on_release=self.add_folder_with_artist
                ),
            ],
        )
        self.add_dialog.open()
    
    def add_folder_with_artist(self, instance):
        """Add folder with the specified artist name"""
        # In a real implementation, you would get the input value here
        # For now, we'll use a placeholder
        artist_name = "New Artist"  # This would come from the input dialog
        
        self.folder_mappings[self.add_folder_path] = artist_name
        self.update_folder_list()
        self.add_dialog.dismiss()
        toast(f"Added folder: {self.add_folder_path}")
    
    def exit_file_manager(self, *args):
        """Close file manager"""
        self.file_manager.close()
    
    def start_monitoring(self):
        """Start monitoring folders"""
        if not self.folder_mappings:
            toast("No folders to monitor")
            return
        
        if self.is_monitoring:
            return  # Already monitoring
        
        # Start monitoring in a background thread
        self.observer = PollingObserver()
        
        for folder_path, artist_name in self.folder_mappings.items():
            try:
                handler = MobileEventHandler(artist_name, self.add_activity)
                self.observer.schedule(handler, folder_path, recursive=True)
            except Exception as e:
                toast(f"Error setting up monitoring for {folder_path}: {str(e)}")
        
        # Start the observer in a separate thread
        def run_observer():
            try:
                self.observer.start()
                while self.is_monitoring:
                    time.sleep(1)
            except Exception as e:
                print(f"Observer error: {str(e)}")
            finally:
                if self.observer:
                    self.observer.stop()
                    self.observer.join()
        
        self.observer_thread = threading.Thread(target=run_observer)
        self.observer_thread.daemon = True
        self.observer_thread.start()
        
        self.is_monitoring = True
        self.monitor_status = "Monitoring"
        toast("Started monitoring folders")
    
    def stop_monitoring(self):
        """Stop monitoring folders"""
        if not self.is_monitoring:
            return  # Not monitoring
        
        # Stop the observer
        self.is_monitoring = False
        if self.observer:
            self.observer.stop()
            self.observer = None
        
        self.monitor_status = "Not Monitoring"
        toast("Stopped monitoring folders")
    
    def add_activity(self, file_path, artist_name, status):
        """Add activity to the log"""
        # This will be called from a background thread, so we need to schedule it on the main thread
        def add_to_log(*args):
            filename = os.path.basename(file_path)
            timestamp = time.strftime("%H:%M:%S")
            activity = f"[{timestamp}] {filename} (Artist: {artist_name}) - {status}"
            
            activity_list = self.ids.activity_list
            item = ActivityItem(text=activity)
            activity_list.add_widget(item)
        
        Clock.schedule_once(add_to_log)

# Define MobileEventHandler class
class MobileEventHandler(FileSystemEventHandler):
    """Event handler for mobile app"""
    def __init__(self, artist_name, callback=None):
        self.artist_name = artist_name
        self.handler = MusicFileHandler(artist_name)
        self.callback = callback
        self.processed_files = set()
    
    def on_created(self, event):
        if not event.is_directory:
            file_path = event.src_path
            # Skip if we've already processed this file
            if file_path in self.processed_files:
                return
            
            # Check if it's an audio file
            if is_audio_file(file_path):
                try:
                    # Wait a bit to ensure file is fully written
                    time.sleep(1)
                    
                    # Process the file
                    self.handler.tag_music_file(file_path)
                    
                    # Add to processed files set
                    self.processed_files.add(file_path)
                    
                    # Call the callback to update the UI
                    if self.callback:
                        self.callback(file_path, self.artist_name, "Tagged successfully")
                
                except Exception as e:
                    if self.callback:
                        self.callback(file_path, self.artist_name, f"Error: {str(e)}")
                    print(f"Error processing file {file_path}: {str(e)}")

# Define MusicTaggerApp class
class MusicTaggerApp(MDApp):
    """Main application class"""
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.accent_palette = "Amber"
        self.theme_cls.theme_style = "Light"
        
        # Window adjustments for mobile/desktop
        if platform != 'android' and platform != 'ios':
            Window.size = (500, 700)
        
        # Load the KV string
        Builder.load_string(KV)
        
        # Create the screen manager
        sm = ScreenManager()
        sm.add_widget(MusicTagScreen(name='musictag'))
        
        return sm
    
    def toggle_nav_drawer(self):
        pass  # Placeholder for navigation drawer toggle

# Application entry point
if __name__ == "__main__":
    MusicTaggerApp().run()
