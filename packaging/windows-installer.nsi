; NSIS Installer Script for Ahoy Indie Media
; Creates a Windows installer EXE with Start Menu shortcuts

!include "MUI2.nsh"

; App Information
!define APP_NAME "Ahoy Indie Media"
!define APP_VERSION "0.2.0"
!define APP_PUBLISHER "Ahoy Indie Media"
!define APP_WEB_SITE "https://ahoy-indie-media.onrender.com"
!define APP_EXECUTABLE "AhoyIndieMedia.exe"
!define APP_INSTALL_DIR "$PROGRAMFILES\${APP_NAME}"
!define APP_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"

; Installer Settings
Name "${APP_NAME}"
OutFile "..\dist\${APP_NAME}-Setup.exe"
InstallDir "${APP_INSTALL_DIR}"
RequestExecutionLevel admin
Unicode True

; Compression
SetCompressor /SOLID lzma

; Version Info
VIProductVersion "${APP_VERSION}.0"
VIAddVersionKey "ProductName" "${APP_NAME}"
VIAddVersionKey "FileDescription" "${APP_NAME} Installer"
VIAddVersionKey "FileVersion" "${APP_VERSION}"
VIAddVersionKey "ProductVersion" "${APP_VERSION}"
VIAddVersionKey "LegalCopyright" "© ${APP_PUBLISHER}"
VIAddVersionKey "CompanyName" "${APP_PUBLISHER}"

; Interface Settings
!define MUI_ICON "icons\ahoy.ico"
!define MUI_UNICON "icons\ahoy.ico"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "icons\ahoy-header.bmp"
!define MUI_WELCOMEFINISHPAGE_BITMAP "icons\ahoy-wizard.bmp"

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "..\LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!define MUI_FINISHPAGE_RUN "$INSTDIR\${APP_EXECUTABLE}"
!define MUI_FINISHPAGE_RUN_TEXT "Launch ${APP_NAME}"
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Languages
!insertmacro MUI_LANGUAGE "English"

; Installer Section
Section "MainSection" SEC01
    SetOutPath "$INSTDIR"
    
    ; Install main executable
    File "..\dist\${APP_EXECUTABLE}"
    
    ; Install app files (if using onefile, this is just the exe)
    ; If using onedir, copy all files:
    ; File /r "..\dist\${APP_NAME}\*"
    
    ; Create Start Menu shortcuts
    CreateDirectory "$SMPROGRAMS\${APP_NAME}"
    CreateShortcut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" "$INSTDIR\${APP_EXECUTABLE}"
    CreateShortcut "$SMPROGRAMS\${APP_NAME}\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
    
    ; Create Desktop shortcut
    CreateShortcut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\${APP_EXECUTABLE}"
    
    ; Write uninstaller
    WriteUninstaller "$INSTDIR\Uninstall.exe"
    
    ; Write registry keys for Add/Remove Programs
    WriteRegStr HKLM "${APP_UNINST_KEY}" "DisplayName" "${APP_NAME}"
    WriteRegStr HKLM "${APP_UNINST_KEY}" "UninstallString" "$INSTDIR\Uninstall.exe"
    WriteRegStr HKLM "${APP_UNINST_KEY}" "InstallLocation" "$INSTDIR"
    WriteRegStr HKLM "${APP_UNINST_KEY}" "DisplayVersion" "${APP_VERSION}"
    WriteRegStr HKLM "${APP_UNINST_KEY}" "Publisher" "${APP_PUBLISHER}"
    WriteRegStr HKLM "${APP_UNINST_KEY}" "URLInfoAbout" "${APP_WEB_SITE}"
    WriteRegDWORD HKLM "${APP_UNINST_KEY}" "NoModify" 1
    WriteRegDWORD HKLM "${APP_UNINST_KEY}" "NoRepair" 1
    
    ; Calculate size
    ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
    IntFmt $0 "0x%08X" $0
    WriteRegDWORD HKLM "${APP_UNINST_KEY}" "EstimatedSize" "$0"
SectionEnd

; Uninstaller Section
Section "Uninstall"
    ; Remove files
    Delete "$INSTDIR\${APP_EXECUTABLE}"
    Delete "$INSTDIR\Uninstall.exe"
    
    ; Remove shortcuts
    Delete "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk"
    Delete "$SMPROGRAMS\${APP_NAME}\Uninstall.lnk"
    RMDir "$SMPROGRAMS\${APP_NAME}"
    Delete "$DESKTOP\${APP_NAME}.lnk"
    
    ; Remove installation directory
    RMDir /r "$INSTDIR"
    
    ; Remove registry keys
    DeleteRegKey HKLM "${APP_UNINST_KEY}"
SectionEnd

