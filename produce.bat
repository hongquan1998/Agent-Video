@echo off
setlocal

:: Set Project Paths
set "PROJECT_DIR=%~dp0"
set "PYTHON_EXE=C:\Users\Admin\AppData\Local\Programs\Python\Python312\python.exe"
set "FFMPEG_DIR=C:\Users\Admin\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin"

:: Append FFmpeg to PATH if present
if exist "%FFMPEG_DIR%" (
    set "PATH=%FFMPEG_DIR%;%PATH%"
)

:: Check for Python
if not exist "%PYTHON_EXE%" (
    set "PYTHON_EXE=python"
)

:: Check Input Argument
if "%~1"=="" (
    echo [ERROR] No audio file provided!
    echo Usage: produce.bat "path\to\voiceover.mp3" [output.mp4] [lang] [storyboard.json]
    echo Example: produce.bat "audio\voice_en.mp3" "output\video.mp4" "en" "storyboard.json"
    exit /b 1
)

set "FIRST_INPUT=%~1"
set "OUTPUT_MP4=%~2"
set "LANG_PARAM=%~3"
set "EXTRA_PARAM=%~4"

if "%LANG_PARAM%"=="" (
    set "LANG_PARAM=auto"
)

if "%FIRST_INPUT:~-5%"==".json" (
    set "CMD_ARGS=--storyboard "%FIRST_INPUT%" --lang "%LANG_PARAM%""
) else if "%FIRST_INPUT:~-3%"==".py" (
    set "CMD_ARGS=--script "%FIRST_INPUT%" --lang "%LANG_PARAM%""
) else (
    set "CMD_ARGS=--audio "%FIRST_INPUT%" --lang "%LANG_PARAM%""
)

if not "%OUTPUT_MP4%"=="" (
    set "CMD_ARGS=%CMD_ARGS% --output "%OUTPUT_MP4%""
)
if not "%EXTRA_PARAM%"=="" (
    if "%EXTRA_PARAM:~-5%"==".json" (
        set "CMD_ARGS=%CMD_ARGS% --storyboard "%EXTRA_PARAM%""
    ) else if "%EXTRA_PARAM:~-3%"==".py" (
        set "CMD_ARGS=%CMD_ARGS% --script "%EXTRA_PARAM%""
    )
)

echo Starting Automated 2D Cinematic Documentary Production...
"%PYTHON_EXE%" "%PROJECT_DIR%src\auto_produce.py" %CMD_ARGS%

if %ERRORLEVEL% equ 0 (
    echo [SUCCESS] Production completed successfully!
) else (
    echo [ERROR] Production failed with error code %ERRORLEVEL%.
)
endlocal
