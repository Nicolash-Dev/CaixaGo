#define MyAppName "CaixaGo"
#define MyAppVersion "0.1.0"
#define MyAppPublisher "CaixaGo"
#define MyAppExeName "CaixaGo.exe"

[Setup]
AppId={{4C9F9442-3F53-4F0D-A9E4-CAIXAGO010001}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}

DefaultDirName={autopf}\CaixaGo
DefaultGroupName=CaixaGo

DisableProgramGroupPage=yes

PrivilegesRequired=admin

OutputDir=output
OutputBaseFilename=CaixaGo-Setup-0.1.0

SetupIconFile=..\app\assets\icons\caixago.ico
UninstallDisplayIcon={app}\CaixaGo.exe

Compression=lzma2
SolidCompression=yes

WizardStyle=modern

ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

VersionInfoVersion=0.1.0.0
VersionInfoCompany=CaixaGo
VersionInfoDescription=CaixaGo - Gestão Inteligente de Caixa
VersionInfoProductName=CaixaGo
VersionInfoProductVersion=0.1.0
VersionInfoCopyright=Copyright © 2026 CaixaGo

CloseApplications=yes
RestartApplications=no

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na Área de Trabalho"; GroupDescription: "Atalhos adicionais:"; Flags: unchecked

[Files]
Source: "..\dist\CaixaGo\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\CaixaGo"; Filename: "{app}\CaixaGo.exe"; WorkingDir: "{app}"
Name: "{autodesktop}\CaixaGo"; Filename: "{app}\CaixaGo.exe"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{app}\CaixaGo.exe"; Description: "Abrir CaixaGo"; Flags: nowait postinstall skipifsilent