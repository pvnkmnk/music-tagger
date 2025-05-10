#!/usr/bin/env python3
import os
import sys
import time
import configparser
import logging
import platform
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QTableWidget, QTableWidgetItem, QFileDialog, 
                            QInputDialog, QMessageBox, QSystemTrayIcon, QMenu, QAction, 
                            QHeaderView, QAbstractItemView, QCheckBox, QTabWidget, QFrame,
                            QStyleFactory)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSettings, QSize
from PyQt5.QtGui import QIcon, QFont, QPixmap, QColor

# Material design theme
try:
    from qt_material import apply_stylesheet
    HAVE_MATERIAL = True
except ImportError:
    HAVE_MATERIAL = False
    print("Qt Material library not found. Using default style.")

# Import the music tagger core functionality
from music_tagger import MusicFileHandler
from audio_utils import is_audio_file
from watchdog.observers.polling import PollingObserver as Observer
from watchdog.events import FileSystemEventHandler

# Configure logging
logging.basicConfig(
    filename='music_tagger_gui.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Event handler with GUI support
class GUIEventHandler(FileSystemEventHandler):
    def __init__(self, artist_name, callback=None):
        self.artist_name = artist_name
        self.handler = MusicFileHandler(artist_name)
        self.callback = callback  # Callback to update the GUI
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
                    
                    # Call the callback to update the GUI
                    if self.callback:
                        relative_path = os.path.relpath(file_path, os.path.dirname(os.path.dirname(file_path)))
                        self.callback(file_path, self.artist_name, "Tagged successfully")
                        
                except Exception as e:
                    if self.callback:
                        self.callback(file_path, self.artist_name, f"Error: {str(e)}")
                    logging.error(f"Error processing file {file_path}: {str(e)}")

# Observer thread for background processing
class ObserverThread(QThread):
    signal_file_processed = pyqtSignal(str, str, str)  # filepath, artist, status
    
    def __init__(self, folder_mappings):
        super().__init__()
        self.folder_mappings = folder_mappings
        self.observer = None
        self.is_running = False
        
    def callback(self, filepath, artist, status):
        self.signal_file_processed.emit(filepath, artist, status)
        
    def run(self):
        self.observer = Observer()
        
        # Set up handlers for each folder
        for folder_path, artist_name in self.folder_mappings.items():
            handler = GUIEventHandler(artist_name, self.callback)
            self.observer.schedule(handler, folder_path, recursive=True)
            
        self.observer.start()
        self.is_running = True
        
        # Keep thread running
        try:
            while self.is_running:
                time.sleep(1)
        except Exception as e:
            logging.error(f"Observer thread error: {str(e)}")
        finally:
            self.stop()
            
    def stop(self):
        self.is_running = False
        if self.observer:
            self.observer.stop()
            self.observer.join()

# Main application window
class MusicTaggerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Application settings
        self.settings = QSettings("JanuaryDecember", "MusicTagger")
        self.folder_mappings = {}
        self.observer_thread = None
        
        # UI setup
        self.setup_ui()
        
        # Load configuration
        self.load_config()
        
        # Create system tray
        self.setup_tray()
        
    def setup_ui(self):
        self.setWindowTitle("Music Tagger")
        self.setMinimumSize(800, 600)
        
        # Restore window geometry
        if self.settings.contains("geometry"):
            self.restoreGeometry(self.settings.value("geometry"))
        else:
            self.setGeometry(100, 100, 800, 600)
        
        # Create main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)
        
        # Dashboard tab
        dashboard_widget = QWidget()
        dashboard_layout = QVBoxLayout(dashboard_widget)
        tab_widget.addTab(dashboard_widget, "Dashboard")
        
        # Status section
        status_section = QWidget()
        status_layout = QHBoxLayout(status_section)
        
        self.status_label = QLabel("Status: Not Monitoring")
        status_layout.addWidget(self.status_label)
        
        self.start_button = QPushButton("Start Monitoring")
        self.start_button.clicked.connect(self.start_monitoring)
        status_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("Stop Monitoring")
        self.stop_button.clicked.connect(self.stop_monitoring)
        self.stop_button.setEnabled(False)
        status_layout.addWidget(self.stop_button)
        
        dashboard_layout.addWidget(status_section)
        
        # Table for folder mappings
        self.folders_table = QTableWidget(0, 3)  # rows, columns
        self.folders_table.setHorizontalHeaderLabels(["Folder Path", "Artist Name", "Actions"])
        self.folders_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.folders_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.folders_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.folders_table.verticalHeader().setVisible(False)
        dashboard_layout.addWidget(self.folders_table)
        
        # Buttons section
        buttons_section = QWidget()
        buttons_layout = QHBoxLayout(buttons_section)
        
        add_button = QPushButton("Add Folder")
        add_button.clicked.connect(self.add_folder)
        buttons_layout.addWidget(add_button)
        
        save_button = QPushButton("Save Configuration")
        save_button.clicked.connect(self.save_config)
        buttons_layout.addWidget(save_button)
        
        dashboard_layout.addWidget(buttons_section)
        
        # Activity log tab
        log_widget = QWidget()
        log_layout = QVBoxLayout(log_widget)
        tab_widget.addTab(log_widget, "Activity Log")
        
        # Activity table
        self.activity_table = QTableWidget(0, 4)  # rows, columns
        self.activity_table.setHorizontalHeaderLabels(["Timestamp", "File", "Artist", "Status"])
        self.activity_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.activity_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.activity_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.activity_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.activity_table.verticalHeader().setVisible(False)
        self.activity_table.setEditTriggers(QAbstractItemView.NoEditTriggers)  # Read-only
        log_layout.addWidget(self.activity_table)
        
        # Settings tab
        settings_widget = QWidget()
        settings_layout = QVBoxLayout(settings_widget)
        tab_widget.addTab(settings_widget, "Settings")
        
        # Run on startup option
        self.startup_checkbox = QCheckBox("Run on system startup")
        self.startup_checkbox.setChecked(self.settings.value("run_on_startup", False, type=bool))
        self.startup_checkbox.stateChanged.connect(self.toggle_startup)
        settings_layout.addWidget(self.startup_checkbox)
        
        # Minimize to tray option
        self.minimize_checkbox = QCheckBox("Minimize to system tray")
        self.minimize_checkbox.setChecked(self.settings.value("minimize_to_tray", True, type=bool))
        self.minimize_checkbox.stateChanged.connect(self.toggle_minimize)
        settings_layout.addWidget(self.minimize_checkbox)
        
        # Add a spacer
        settings_layout.addStretch()
        
        # About section
        about_label = QLabel("Music Tagger\nVersion 1.0.0\nCreated by januarydecember")
        about_label.setAlignment(Qt.AlignCenter)
        settings_layout.addWidget(about_label)
        
    def setup_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        
        # Use a standard app icon from the system
        self.tray_icon.setIcon(self.style().standardIcon(QApplication.style().SP_MediaPlay))
        
        # Create tray menu
        tray_menu = QMenu()
        
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        hide_action = QAction("Hide", self)
        hide_action.triggered.connect(self.hide)
        tray_menu.addAction(hide_action)
        
        toggle_monitor = QAction("Start Monitoring", self)
        toggle_monitor.triggered.connect(self.toggle_monitoring)
        tray_menu.addAction(toggle_monitor)
        self.toggle_monitor_action = toggle_monitor
        
        tray_menu.addSeparator()
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QApplication.instance().quit)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        # Connect double-click to show/hide
        self.tray_icon.activated.connect(self.tray_activated)
        
    def tray_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            if self.isVisible():
                self.hide()
            else:
                self.show()
                self.activateWindow()
    
    def closeEvent(self, event):
        if self.minimize_checkbox.isChecked():
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                "Music Tagger",
                "Application has been minimized to the system tray.",
                QSystemTrayIcon.Information,
                2000
            )
        else:
            self.save_settings()
            event.accept()
            
    def save_settings(self):
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("run_on_startup", self.startup_checkbox.isChecked())
        self.settings.setValue("minimize_to_tray", self.minimize_checkbox.isChecked())
        
    def toggle_startup(self, state):
        is_enabled = state == Qt.Checked
        self.settings.setValue("run_on_startup", is_enabled)
        
        # Create or remove startup shortcut based on the OS
        if sys.platform == "win32":
            try:
                import winreg
                startup_key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER, 
                    r"Software\Microsoft\Windows\CurrentVersion\Run", 
                    0, 
                    winreg.KEY_SET_VALUE
                )
                
                if is_enabled:
                    # Add to startup
                    winreg.SetValueEx(
                        startup_key, 
                        "MusicTagger", 
                        0, 
                        winreg.REG_SZ, 
                        f'"{sys.executable}" "{os.path.abspath(__file__)}" --minimized'
                    )
                else:
                    # Remove from startup
                    try:
                        winreg.DeleteValue(startup_key, "MusicTagger")
                    except WindowsError:
                        pass
                        
                winreg.CloseKey(startup_key)
            except Exception as e:
                logging.error(f"Failed to set startup option: {str(e)}")
                QMessageBox.warning(self, "Error", f"Failed to set startup option: {str(e)}")
        elif sys.platform == "darwin":  # macOS
            plist_path = os.path.expanduser("~/Library/LaunchAgents/com.januarydecember.musictagger.plist")
            
            if is_enabled:
                # Create plist file for macOS
                plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.januarydecember.musictagger</string>
    <key>ProgramArguments</key>
    <array>
        <string>{sys.executable}</string>
        <string>{os.path.abspath(__file__)}</string>
        <string>--minimized</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
"""
                try:
                    with open(plist_path, "w") as f:
                        f.write(plist_content)
                except Exception as e:
                    logging.error(f"Failed to create startup plist: {str(e)}")
                    QMessageBox.warning(self, "Error", f"Failed to set startup option: {str(e)}")
            else:
                # Remove plist file
                if os.path.exists(plist_path):
                    try:
                        os.remove(plist_path)
                    except Exception as e:
                        logging.error(f"Failed to remove startup plist: {str(e)}")
                        QMessageBox.warning(self, "Error", f"Failed to disable startup option: {str(e)}")
        else:  # Linux
            desktop_file_path = os.path.expanduser("~/.config/autostart/musictagger.desktop")
            
            if is_enabled:
                # Create desktop file for Linux
                desktop_content = f"""[Desktop Entry]
Type=Application
Name=Music Tagger
Exec={sys.executable} {os.path.abspath(__file__)} --minimized
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
"""
                try:
                    os.makedirs(os.path.dirname(desktop_file_path), exist_ok=True)
                    with open(desktop_file_path, "w") as f:
                        f.write(desktop_content)
                except Exception as e:
                    logging.error(f"Failed to create startup desktop file: {str(e)}")
                    QMessageBox.warning(self, "Error", f"Failed to set startup option: {str(e)}")
            else:
                # Remove desktop file
                if os.path.exists(desktop_file_path):
                    try:
                        os.remove(desktop_file_path)
                    except Exception as e:
                        logging.error(f"Failed to remove startup desktop file: {str(e)}")
                        QMessageBox.warning(self, "Error", f"Failed to disable startup option: {str(e)}")
    
    def toggle_minimize(self, state):
        self.settings.setValue("minimize_to_tray", state == Qt.Checked)
    
    def toggle_monitoring(self):
        if self.observer_thread and self.observer_thread.is_running:
            self.stop_monitoring()
        else:
            self.start_monitoring()
    
    def load_config(self):
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
        
        if not os.path.exists(config_path):
            return
            
        try:
            config = configparser.ConfigParser()
            config.read(config_path)
            
            # Clear current folder mappings
            self.folder_mappings = {}
            
            # Parse folder-artist mappings
            if 'Folders' in config:
                for folder_path, artist_name in config['Folders'].items():
                    folder_path = folder_path.strip()
                    artist_name = artist_name.strip()
                    self.folder_mappings[folder_path] = artist_name
                    
            # Update the folders table
            self.update_folders_table()
            
        except Exception as e:
            logging.error(f"Error loading configuration: {str(e)}")
            QMessageBox.warning(self, "Error", f"Failed to load configuration: {str(e)}")
    
    def save_config(self):
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
        
        try:
            config = configparser.ConfigParser()
            config['MusicTagger'] = {'log_level': 'INFO'}
            
            # Add folder mappings
            config['Folders'] = {}
            for folder_path, artist_name in self.folder_mappings.items():
                config['Folders'][folder_path] = artist_name
                
            # Write to file
            with open(config_path, 'w') as f:
                config.write(f)
                
            QMessageBox.information(self, "Success", "Configuration saved successfully.")
            
        except Exception as e:
            logging.error(f"Error saving configuration: {str(e)}")
            QMessageBox.warning(self, "Error", f"Failed to save configuration: {str(e)}")
    
    def update_folders_table(self):
        # Clear the table
        self.folders_table.setRowCount(0)
        
        # Add current folder mappings
        row = 0
        for folder_path, artist_name in self.folder_mappings.items():
            self.folders_table.insertRow(row)
            
            # Folder path
            self.folders_table.setItem(row, 0, QTableWidgetItem(folder_path))
            
            # Artist name
            self.folders_table.setItem(row, 1, QTableWidgetItem(artist_name))
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(4, 0, 4, 0)
            
            # Edit button
            edit_button = QPushButton("Edit")
            edit_button.setProperty("folder_path", folder_path)
            edit_button.clicked.connect(lambda _, fp=folder_path: self.edit_folder(fp))
            actions_layout.addWidget(edit_button)
            
            # Remove button
            remove_button = QPushButton("Remove")
            remove_button.setProperty("folder_path", folder_path)
            remove_button.clicked.connect(lambda _, fp=folder_path: self.remove_folder(fp))
            actions_layout.addWidget(remove_button)
            
            self.folders_table.setCellWidget(row, 2, actions_widget)
            
            row += 1
    
    def add_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder to Monitor")
        if not folder_path:
            return
            
        artist_name, ok = QInputDialog.getText(self, "Artist Name", "Enter artist name for this folder:")
        if not ok or not artist_name:
            return
            
        # Add to folder mappings
        self.folder_mappings[folder_path] = artist_name
        
        # Update the table
        self.update_folders_table()
        
        # Auto-save config
        self.save_config()
    
    def edit_folder(self, folder_path):
        if folder_path not in self.folder_mappings:
            return
            
        artist_name, ok = QInputDialog.getText(
            self, "Edit Artist Name", 
            "Enter new artist name for this folder:", 
            text=self.folder_mappings[folder_path]
        )
        
        if not ok or not artist_name:
            return
            
        # Update folder mapping
        self.folder_mappings[folder_path] = artist_name
        
        # Update the table
        self.update_folders_table()
        
        # Auto-save config
        self.save_config()
    
    def remove_folder(self, folder_path):
        if folder_path not in self.folder_mappings:
            return
            
        reply = QMessageBox.question(
            self, "Confirm Removal", 
            f"Are you sure you want to remove the folder '{folder_path}'?",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
            
        # Remove folder mapping
        del self.folder_mappings[folder_path]
        
        # Update the table
        self.update_folders_table()
        
        # Auto-save config
        self.save_config()
    
    def start_monitoring(self):
        if not self.folder_mappings:
            QMessageBox.warning(self, "Error", "No folders configured. Please add at least one folder to monitor.")
            return
            
        if self.observer_thread and self.observer_thread.is_running:
            return  # Already running
            
        # Create and start observer thread
        self.observer_thread = ObserverThread(self.folder_mappings)
        self.observer_thread.signal_file_processed.connect(self.file_processed)
        self.observer_thread.start()
        
        # Update UI
        self.status_label.setText("Status: Monitoring")
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.toggle_monitor_action.setText("Stop Monitoring")
        
        # Show notification
        self.tray_icon.showMessage(
            "Music Tagger",
            f"Started monitoring {len(self.folder_mappings)} folders",
            QSystemTrayIcon.Information,
            2000
        )
    
    def stop_monitoring(self):
        if not self.observer_thread or not self.observer_thread.is_running:
            return  # Not running
            
        # Stop observer thread
        self.observer_thread.stop()
        self.observer_thread = None
        
        # Update UI
        self.status_label.setText("Status: Not Monitoring")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.toggle_monitor_action.setText("Start Monitoring")
        
        # Show notification
        self.tray_icon.showMessage(
            "Music Tagger",
            "Stopped monitoring folders",
            QSystemTrayIcon.Information,
            2000
        )
    
    def file_processed(self, filepath, artist, status):
        # Add to activity log
        row = 0
        self.activity_table.insertRow(row)
        
        # Timestamp
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        self.activity_table.setItem(row, 0, QTableWidgetItem(timestamp))
        
        # File path (show only filename and parent folder)
        filename = os.path.basename(filepath)
        parent = os.path.basename(os.path.dirname(filepath))
        display_path = f"{parent}/{filename}"
        self.activity_table.setItem(row, 1, QTableWidgetItem(display_path))
        
        # Artist
        self.activity_table.setItem(row, 2, QTableWidgetItem(artist))
        
        # Status
        self.activity_table.setItem(row, 3, QTableWidgetItem(status))
        
        # Show notification for errors
        if status.startswith("Error"):
            self.tray_icon.showMessage(
                "Music Tagger - Error",
                f"Failed to tag file: {display_path}",
                QSystemTrayIcon.Warning,
                2000
            )

# Application entry point
def main():
    # Check command line arguments
    start_minimized = "--minimized" in sys.argv
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Music Tagger")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("JanuaryDecember")
    
    # Create main window
    window = MusicTaggerApp()
    
    # Apply Material Design theme if available
    if HAVE_MATERIAL:
        try:
            # Apply one of the qt-material themes
            apply_stylesheet(app, theme='dark_teal.xml')
            print("Applied Material Design theme: dark_teal")
            
            # You can choose from several themes:
            # 'dark_amber.xml'
            # 'dark_blue.xml'
            # 'dark_cyan.xml'
            # 'dark_lightgreen.xml'
            # 'dark_pink.xml'
            # 'dark_purple.xml'
            # 'dark_red.xml'
            # 'dark_teal.xml'
            # 'dark_yellow.xml'
            # 'light_amber.xml'
            # 'light_blue.xml'
            # 'light_cyan.xml'
            # 'light_cyan_500.xml'
            # 'light_lightgreen.xml'
            # 'light_pink.xml'
            # 'light_purple.xml'
            # 'light_red.xml'
            # 'light_teal.xml'
            # 'light_yellow.xml'
        except Exception as e:
            print(f"Error applying Material theme: {str(e)}")
            print("Falling back to Fusion style")
            app.setStyle("Fusion")
            
            # Create a modern dark palette manually
            palette = app.palette()
            palette.setColor(palette.Window, QColor(53, 53, 53))
            palette.setColor(palette.WindowText, Qt.white)
            palette.setColor(palette.Base, QColor(25, 25, 25))
            palette.setColor(palette.AlternateBase, QColor(53, 53, 53))
            palette.setColor(palette.ToolTipBase, Qt.white)
            palette.setColor(palette.ToolTipText, Qt.white)
            palette.setColor(palette.Text, Qt.white)
            palette.setColor(palette.Button, QColor(53, 53, 53))
            palette.setColor(palette.ButtonText, Qt.white)
            palette.setColor(palette.BrightText, Qt.red)
            palette.setColor(palette.Link, QColor(42, 130, 218))
            palette.setColor(palette.Highlight, QColor(42, 130, 218))
            palette.setColor(palette.HighlightedText, Qt.black)
            app.setPalette(palette)
    else:
        # Fall back to Fusion style with a dark theme if material theme not available
        print("Material Design theme not available, using custom Fusion style")
        app.setStyle("Fusion")
        
        # Create a modern dark palette
        palette = app.palette()
        palette.setColor(palette.Window, QColor(53, 53, 53))
        palette.setColor(palette.WindowText, Qt.white)
        palette.setColor(palette.Base, QColor(25, 25, 25))
        palette.setColor(palette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(palette.ToolTipBase, Qt.white)
        palette.setColor(palette.ToolTipText, Qt.white)
        palette.setColor(palette.Text, Qt.white)
        palette.setColor(palette.Button, QColor(53, 53, 53))
        palette.setColor(palette.ButtonText, Qt.white)
        palette.setColor(palette.BrightText, Qt.red)
        palette.setColor(palette.Link, QColor(42, 130, 218))
        palette.setColor(palette.Highlight, QColor(42, 130, 218))
        palette.setColor(palette.HighlightedText, Qt.black)
        app.setPalette(palette)
    
    if start_minimized:
        # Start the application minimized to tray
        if window.settings.value("minimize_to_tray", True, type=bool):
            pass  # Don't show the window
        else:
            window.show()
            window.setWindowState(Qt.WindowMinimized)
    else:
        window.show()
    
    # Start monitoring on launch if configured
    if window.settings.value("start_on_launch", True, type=bool):
        window.start_monitoring()
    
    # Run the application
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
