$WshShell = New-Object -ComObject WScript.Shell

# Get the current script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$batchFilePath = Join-Path $scriptDir "start_background_monitor.bat"

# Get the startup folder path
$startupFolder = $WshShell.SpecialFolders("Startup")
$shortcutPath = Join-Path $startupFolder "Music Tagger.lnk"

# Create the shortcut
$Shortcut = $WshShell.CreateShortcut($shortcutPath)
$Shortcut.TargetPath = $batchFilePath
$Shortcut.Description = "Start Music Tagger Background Monitor"
$Shortcut.WorkingDirectory = $scriptDir
$Shortcut.IconLocation = "shell32.dll,296"  # Music icon from Windows shell
$Shortcut.Save()

Write-Host "Shortcut created: $shortcutPath"
Write-Host "Music Tagger will now start automatically when you boot your computer."
