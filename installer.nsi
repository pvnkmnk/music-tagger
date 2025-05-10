; Music Tagger Installer Script
; Created for NSIS 3.0 or higher

!define APPNAME "Music Tagger"
!define COMPANYNAME "JanuaryDecember"
!define DESCRIPTION "Automatic music file tagger with Material Design"
!define VERSION "1.0.0"
!define COPYRIGHT "© 2025 JanuaryDecember"
!define INSTALLSIZE 45000  ; Approximate size in KB

; Include modern UI elements
!include "MUI2.nsh"
!include "FileFunc.nsh"

; General settings
Name "${APPNAME}"
Caption "${APPNAME} ${VERSION} Setup"
OutFile "MusicTagger-${VERSION}-Setup.exe"
InstallDir "$PROGRAMFILES\${COMPANYNAME}\${APPNAME}"
InstallDirRegKey HKLM "Software\${COMPANYNAME}\${APPNAME}" ""
RequestExecutionLevel admin  ; Request admin privileges

; Interface settings
!define MUI_ABORTWARNING

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_INSTFILES
!define MUI_FINISHPAGE_RUN "$INSTDIR\MusicTagger.exe"
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Languages
!insertmacro MUI_LANGUAGE "English"

; Install sections
Section "Music Tagger" SecMain
    SectionIn RO  ; Required section, cannot be deselected
    SetOutPath "$INSTDIR"
    
    ; Copy all files from the build directory
    File /r "dist\MusicTagger\*.*"
    
    ; Create uninstaller
    WriteUninstaller "$INSTDIR\Uninstall.exe"
    
    ; Create shortcuts
    CreateDirectory "$SMPROGRAMS\${COMPANYNAME}"
    CreateShortcut "$SMPROGRAMS\${COMPANYNAME}\${APPNAME}.lnk" "$INSTDIR\MusicTagger.exe"
    CreateShortcut "$SMPROGRAMS\${COMPANYNAME}\Uninstall ${APPNAME}.lnk" "$INSTDIR\Uninstall.exe"
    CreateShortcut "$DESKTOP\${APPNAME}.lnk" "$INSTDIR\MusicTagger.exe"
    
    ; Write registry information
    WriteRegStr HKLM "Software\${COMPANYNAME}\${APPNAME}" "" "$INSTDIR"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "DisplayName" "${APPNAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "UninstallString" "$INSTDIR\Uninstall.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "DisplayIcon" "$INSTDIR\MusicTagger.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "Publisher" "${COMPANYNAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "DisplayVersion" "${VERSION}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "URLInfoAbout" "https://github.com/januarydecember/music-tagger"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "HelpLink" "https://github.com/januarydecember/music-tagger/issues"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "NoRepair" 1
    
    ; Calculate and write install size
    ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
    IntFmt $0 "0x%08X" $0
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "EstimatedSize" "$0"
SectionEnd

Section "Start with Windows" SecStartup
    CreateShortCut "$SMSTARTUP\${APPNAME}.lnk" "$INSTDIR\MusicTagger.exe" "--minimized"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Run" "${APPNAME}" "$\"$INSTDIR\MusicTagger.exe$\" --minimized"
SectionEnd

; Descriptions
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecMain} "Install the Music Tagger application."
    !insertmacro MUI_DESCRIPTION_TEXT ${SecStartup} "Start Music Tagger automatically when Windows starts."
!insertmacro MUI_FUNCTION_DESCRIPTION_END

; Uninstaller section
Section "Uninstall"
    ; Remove shortcuts
    Delete "$DESKTOP\${APPNAME}.lnk"
    Delete "$SMSTARTUP\${APPNAME}.lnk"
    Delete "$SMPROGRAMS\${COMPANYNAME}\${APPNAME}.lnk"
    Delete "$SMPROGRAMS\${COMPANYNAME}\Uninstall ${APPNAME}.lnk"
    RMDir "$SMPROGRAMS\${COMPANYNAME}"
    
    ; Remove registry keys
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}"
    DeleteRegKey HKLM "Software\${COMPANYNAME}\${APPNAME}"
    DeleteRegValue HKCU "Software\Microsoft\Windows\CurrentVersion\Run" "${APPNAME}"
    
    ; Remove files and directories
    RMDir /r "$INSTDIR"
SectionEnd
