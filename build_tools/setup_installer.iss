; Script generated for Inno Setup compiler
[Setup]
AppName=Dental Clinic MS
AppVersion=1.3.0
DefaultDirName={autopf}\Clinic MS
DefaultGroupName=Dental Clinic MS
OutputDir=installer_output
OutputBaseFilename=Setup_Clinic_MS_v1.3.0
Compression=lzma
SolidCompression=yes
SetupIconFile=app_icon.ico
UninstallDisplayIcon={app}\Clinic MS v1.3.0.exe

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "dist\Clinic MS v1.3.0.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Clinic MS"; Filename: "{app}\Clinic MS v1.3.0.exe"
Name: "{autodesktop}\Clinic MS"; Filename: "{app}\Clinic MS v1.3.0.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\Clinic MS v1.3.0.exe"; Description: "{cm:LaunchProgram,Clinic MS}"; Flags: nowait postinstall skipifsilent
