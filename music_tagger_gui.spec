# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Music Tagger GUI
"""
import os
import sys
from PyInstaller.utils.hooks import collect_all, collect_submodules

block_cipher = None

# Determine base directory
base_dir = os.path.dirname(os.path.abspath(SPECPATH))

# Collect Qt Material data
try:
    from qt_material import list_themes
    qt_material_data = []
    for theme in list_themes():
        theme_path = os.path.join(os.path.dirname(os.path.abspath(list_themes.__code__.co_filename)), theme)
        if os.path.exists(theme_path):
            qt_material_data.append((theme_path, theme))
except ImportError:
    qt_material_data = []

# Collect additional hiddenimports
hiddenimports = []
hiddenimports.extend(collect_submodules('watchdog'))
hiddenimports.extend(collect_submodules('mutagen'))
hiddenimports.extend(collect_submodules('tinytag'))
hiddenimports.extend(collect_submodules('PyQt5'))
try:
    hiddenimports.extend(collect_submodules('qt_material'))
except ImportError:
    pass

# Define additional binaries and data files
binaries = []
datas = []
datas.extend(qt_material_data)

# Add config.ini.sample
config_path = os.path.join(base_dir, 'config.ini.sample')
if os.path.exists(config_path):
    datas.append((config_path, '.'))
else:
    print(f"Warning: Could not find config.ini.sample at {config_path}")
    # Try to create a basic config.ini.sample if it doesn't exist
    try:
        with open(config_path, 'w') as f:
            f.write("[MusicTagger]\nlog_level = INFO\n\n[Folders]\nC:\\Path\\To\\Your\\Music\\Folder = Artist Name\n")
        print(f"Created basic config.ini.sample at {config_path}")
        datas.append((config_path, '.'))
    except Exception as e:
        print(f"Error creating config.ini.sample: {str(e)}")

# Define the main analysis object
a = Analysis(
    ['music_tagger_gui.py'],
    pathex=[base_dir],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Create the PYZ archive
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Create the executable
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MusicTagger',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # You can add an icon file here if you have one
)

# Create directory structure to collect required files
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas, 
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MusicTagger',
)
