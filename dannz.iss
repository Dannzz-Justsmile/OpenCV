[Setup]
AppName=Dannz
AppVersion=2.0
DefaultDirName={pf}\Dannz
DefaultGroupName=Dannz
OutputBaseFilename=DannzSetup
DisableProgramGroupPage=yes
Compression=lzma
SolidCompression=yes
SetupIconFile=D:\Do not open\Hacker\iphone-simulator-main-20241201T015448Z-001\dist\app.ico
Password=51019158
LicenseFile=D:\Do not open\Hacker\iphone-simulator-main-20241201T015448Z-001\dist\output\LICENSE
InfoAfterFile=D:\Do not open\Hacker\iphone-simulator-main-20241201T015448Z-001\dist\output\README.md
WizardStyle=modern

[Files]
Source: "D:\Do not open\Hacker\iphone-simulator-main-20241201T015448Z-001\dist\output\finger.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "D:\Do not open\Hacker\iphone-simulator-main-20241201T015448Z-001\dist\output\main.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "D:\Do not open\Hacker\iphone-simulator-main-20241201T015448Z-001\dist\output\flap.exe"; DestDir: "{app}"; Flags: ignoreversion



; Required files for main.exe
Source: "D:\Do not open\Hacker\iphone-simulator-main-20241201T015448Z-001\dist\output\face.py"; DestDir: "{app}"
Source: "D:\Do not open\Hacker\iphone-simulator-main-20241201T015448Z-001\dist\output\dlib_face_recognition_resnet_model_v1.dat"; DestDir: "{app}"
Source: "D:\Do not open\Hacker\iphone-simulator-main-20241201T015448Z-001\dist\output\mmod_human_face_detector.dat"; DestDir: "{app}"
Source: "D:\Do not open\Hacker\iphone-simulator-main-20241201T015448Z-001\dist\output\shape_predictor_5_face_landmarks.dat"; DestDir: "{app}"
Source: "D:\Do not open\Hacker\iphone-simulator-main-20241201T015448Z-001\dist\output\shape_predictor_68_face_landmarks.dat"; DestDir: "{app}"

; Required files for flap.exe
Source: "D:\Do not open\Hacker\iphone-simulator-main-20241201T015448Z-001\dist\output\flap.py"; DestDir: "{app}"
Source: "D:\Do not open\Hacker\iphone-simulator-main-20241201T015448Z-001\dist\output\bird.png"; DestDir: "{app}"
Source: "D:\Do not open\Hacker\iphone-simulator-main-20241201T015448Z-001\dist\output\bird_up.png"; DestDir: "{app}"
Source: "D:\Do not open\Hacker\iphone-simulator-main-20241201T015448Z-001\dist\output\bird_down.png"; DestDir: "{app}"
Source: "D:\Do not open\Hacker\iphone-simulator-main-20241201T015448Z-001\dist\output\plane.png"; DestDir: "{app}"
Source: "D:\Do not open\Hacker\iphone-simulator-main-20241201T015448Z-001\dist\output\boss.png"; DestDir: "{app}"
Source: "D:\Do not open\Hacker\iphone-simulator-main-20241201T015448Z-001\dist\output\cloud.png"; DestDir: "{app}"
Source: "D:\Do not open\Hacker\iphone-simulator-main-20241201T015448Z-001\dist\output\bird_boss.png"; DestDir: "{app}"

; Additional files
Source: "D:\Do not open\Hacker\iphone-simulator-main-20241201T015448Z-001\dist\output\LICENSE"; DestDir: "{app}"
Source: "D:\Do not open\Hacker\iphone-simulator-main-20241201T015448Z-001\dist\output\requirement.txt"; DestDir: "{app}"
Source: "D:\Do not open\Hacker\iphone-simulator-main-20241201T015448Z-001\dist\output\README.md"; DestDir: "{app}"
Source: "D:\Do not open\Hacker\iphone-simulator-main-20241201T015448Z-001\dist\output\finger.py"; DestDir: "{app}"
Source: "D:\Do not open\Hacker\iphone-simulator-main-20241201T015448Z-001\dist\output\face.py"; DestDir: "{app}"
Source: "D:\Do not open\Hacker\iphone-simulator-main-20241201T015448Z-001\dist\output\flap.py"; DestDir: "{app}"

[Icons]
Name: "{group}\Dannz"; Filename: "{app}\Dannz.exe"

[Run]
Filename: "{app}\finger.exe"; Description: "Launch Dannz"; Flags: nowait postinstall