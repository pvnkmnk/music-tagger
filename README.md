# Music Tagger

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive application that automatically tags music files with the correct artist name when they're created in or moved to watched folders. Available in multiple versions: console, GUI (Windows/Mac/Linux), and mobile (Android/iOS).

## Table of Contents

- [Features](#features)
- [Available Versions](#available-versions)
  - [Console Version](#console-version)
  - [GUI Version](#gui-version)
  - [Mobile Version](#mobile-version)
- [Installation](#installation)
- [Usage](#usage)
- [How it works](#how-it-works)
- [Building Mobile Apps](#building-mobile-apps)
- [Requirements](#requirements)

## Features

- Monitor multiple folders simultaneously, each with a unique artist name
- Automatically tag new music files with the correct artist metadata
- Works with multiple audio formats: MP3, FLAC, WAV, MIDI
- Available as console app, GUI application, or mobile app
- Cross-platform support (Windows, macOS, Linux, Android, iOS)
- Run silently in the background or as a system service
- System tray integration for desktop platforms

## Available Versions

### Console Version

The original, lightweight version that runs in the terminal. Ideal for servers, headless setups, or users who prefer command-line tools.

- `music_tagger.py` - Standard version
- `music_tagger_background.pyw` - Background version (no console window)
- Windows service support via `install_service.bat`

### GUI Version

A user-friendly desktop application with a graphical interface. Features include:

- Multi-folder monitoring with different artist names
- Start/stop monitoring with visual feedback
- Activity logging with timestamps
- System tray integration for minimal footprint
- Cross-platform compatibility (Windows, macOS, Linux)

Launch with `start_gui.py` or `python music_tagger_gui.py`

### Mobile Version

A touch-friendly mobile application for Android and iOS devices:

- Material Design UI with Kivy/KivyMD
- Monitor folders on your device's storage
- Activity log with real-time updates
- Built using cross-platform technologies

## Installation

### Console Version

1. Clone or download this repository
2. Install the required Python packages:

```bash
pip install -r requirements.txt
```

3. Copy `config.ini.sample` to `config.ini` and edit it to set your folder(s) and artist name(s)

```ini
[MusicTagger]
log_level = INFO

[Folders]
C:\Path\To\Your\Music\Folder = Artist Name
D:\Another\Music\Folder = Different Artist
```

### GUI Version

1. Install the required packages:

```bash
pip install -r requirements.txt
```

2. Run the GUI application:

```bash
python start_gui.py
```

### Mobile Version

#### For Android:

1. Install the required packages for building:

```bash
pip install -r requirements_mobile.txt
```

2. Use Buildozer to create the Android APK:

```bash
buildozer android debug
```

#### For iOS:

iOS builds must be performed on a Mac with Xcode installed:

1. Install the required packages
2. Use the Kivy iOS toolchain to build the app

## Usage

### Option 1: Console Application

Run the application in console mode to see real-time logs:

```bash
python music_tagger.py
```

When prompted:
1. Enter the folder path you want to watch
2. Enter your artist name

### Option 2: Background Application

Run silently in the background:

```bash
start_background_monitor.bat
```

The application will use the settings from `config.ini` and run without a visible window. Activity is logged to `music_tagger_background.log`.

### Auto-start on Boot

To have Music Tagger start automatically when you boot your computer:

```bash
powershell -ExecutionPolicy Bypass -File create_startup_shortcut.ps1
```

This will create a shortcut in your Windows Startup folder.

## Features

✅ **Smart Monitoring**: Real-time monitoring of folders and all subfolders for new music files

✅ **Multi-format Support**:
  - MP3 files (ID3 tags)
  - FLAC files (Vorbis comments)
  - WAV files (direct metadata or companion files)
  - MIDI files (detection with limited tagging)

✅ **Artist Branding**: Automatic embedding of your artist name in file metadata

✅ **Background Operation**: Run silently in the background with automatic startup option

✅ **Smart Error Handling**: Automatic backup before modification with fallback options

✅ **Easy Configuration**: Simple setup with configuration file

## Technical Notes

- Supports file formats: `.mp3`, `.flac`, `.wav`, `.mid`, `.midi`
- MP3 and FLAC files are tagged using industry-standard metadata formats
- WAV files use direct embedding when TagLib is available, or companion files as fallback
- MIDI files are detected but have limited tagging capabilities due to format restrictions
- Recursive monitoring means you only need to specify the parent folder
- Configuration is stored in the `config.ini` file
- Log files provide detailed information about all operations

## Troubleshooting

- **File not being tagged?** Check the log file for error messages
- **Background mode not working?** Try running in console mode to see error output
- **TagLib issues?** The application will automatically fall back to companion file method
- **Path issues?** Make sure to use double backslashes in paths, e.g., `C:\Music\Folder`

## License

MIT License - See [LICENSE](LICENSE) for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

Created by januarydecember - Automatic music tagging for artists, by an artist
