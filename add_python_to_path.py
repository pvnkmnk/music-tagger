#!/usr/bin/env python3
"""
Add Python and installed packages to system PATH
"""
import os
import sys
import site
import winreg
import ctypes
import subprocess
from pathlib import Path

def is_admin():
    """Check if the script is running with admin privileges"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def get_python_paths():
    """Get all relevant Python paths that should be on PATH"""
    paths = []
    
    # Python installation directory
    python_dir = os.path.dirname(sys.executable)
    paths.append(python_dir)
    
    # Scripts directory
    scripts_dir = os.path.join(python_dir, 'Scripts')
    if os.path.exists(scripts_dir):
        paths.append(scripts_dir)
    
    # User scripts directory
    user_base = site.getuserbase()
    user_scripts = os.path.join(user_base, 'Scripts')
    if os.path.exists(user_scripts):
        paths.append(user_scripts)
    
    # Site-packages Scripts directories
    for site_dir in site.getsitepackages():
        site_scripts = os.path.join(site_dir, 'Scripts')
        if os.path.exists(site_scripts):
            paths.append(site_scripts)
    
    # User site-packages
    user_site = site.getusersitepackages()
    if user_site:
        user_site_parent = Path(user_site).parent
        user_site_scripts = os.path.join(user_site_parent, 'Scripts')
        if os.path.exists(user_site_scripts):
            paths.append(user_site_scripts)
    
    # User Python directory from AppData
    appdata_roaming = os.environ.get('APPDATA', '')
    if appdata_roaming:
        python_version = f"Python{sys.version_info.major}{sys.version_info.minor}"
        appdata_scripts = os.path.join(appdata_roaming, 'Python', python_version, 'Scripts')
        if os.path.exists(appdata_scripts):
            paths.append(appdata_scripts)
    
    return paths

def get_current_path():
    """Get the current system PATH"""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment', 0, winreg.KEY_READ)
        path, _ = winreg.QueryValueEx(key, 'PATH')
        winreg.CloseKey(key)
        return path
    except:
        return ""

def set_user_path(new_path):
    """Set the user PATH environment variable"""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment', 0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, 'PATH', 0, winreg.REG_EXPAND_SZ, new_path)
        winreg.CloseKey(key)
        
        # Notify the system about the change
        subprocess.run(['setx', 'PATH', new_path], check=True, capture_output=True)
        return True
    except Exception as e:
        print(f"Error setting PATH: {str(e)}")
        return False

def set_system_path(new_path):
    """Set the system PATH environment variable (requires admin)"""
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment', 0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, 'PATH', 0, winreg.REG_EXPAND_SZ, new_path)
        winreg.CloseKey(key)
        
        # Notify the system about the change
        subprocess.run(['setx', 'PATH', new_path, '/M'], check=True, capture_output=True)
        return True
    except Exception as e:
        print(f"Error setting system PATH: {str(e)}")
        return False

def update_path():
    """Update PATH with Python directories"""
    python_paths = get_python_paths()
    
    # Get current PATH
    current_path = get_current_path()
    path_entries = current_path.split(';') if current_path else []
    
    # Add Python paths if not already in PATH
    added_paths = []
    for path in python_paths:
        normalized_path = os.path.normpath(path.strip())
        if normalized_path and normalized_path not in path_entries:
            path_entries.append(normalized_path)
            added_paths.append(normalized_path)
    
    if not added_paths:
        print("All Python paths are already in PATH. No changes needed.")
        return True
    
    # Create new PATH string
    new_path = ';'.join(path_entries)
    
    # Set the PATH
    if is_admin():
        print("Running as administrator. Updating system-wide PATH...")
        success = set_system_path(new_path)
    else:
        print("Updating user PATH...")
        success = set_user_path(new_path)
    
    if success:
        print("PATH updated successfully.")
        print("\nAdded the following directories:")
        for path in added_paths:
            print(f"  - {path}")
        print("\nYou'll need to restart your command prompts or IDE for the changes to take effect.")
        return True
    else:
        print("Failed to update PATH.")
        return False

def main():
    """Main function"""
    if not is_admin() and '-noelevate' not in sys.argv:
        # Re-run the script with admin privileges
        print("Requesting administrator privileges to update PATH...")
        
        script = os.path.abspath(__file__)
        params = ' '.join([f'"{a}"' for a in sys.argv[1:]])
        
        try:
            # Try to elevate privileges
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, f'"{script}" {params}', None, 1
            )
            return 0
        except:
            print("Failed to get admin privileges. Will try to update user PATH only.")
            sys.argv.append('-noelevate')  # Prevent infinite loop
    
    update_path()
    input("Press Enter to exit...")
    return 0

if __name__ == "__main__":
    sys.exit(main())
