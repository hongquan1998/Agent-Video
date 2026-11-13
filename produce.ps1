param (
    [Parameter(Mandatory=$true, Position=0)]
    [string]$Audio,

    [Parameter(Position=1)]
    [string]$Output,

    [Parameter(Position=2)]
    [string]$Lang = "auto",

    [switch]$PreviewOnly,

    [int]$Fps = 30
)

$ProjectDir = $PSScriptRoot
$PythonExe = "C:\Users\Admin\AppData\Local\Programs\Python\Python312\python.exe"
$FFmpegDir = "C:\Users\Admin\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin"

if (Test-Path $FFmpegDir) {
    $env:Path = "$FFmpegDir;" + $env:Path
}

if (-not (Test-Path $PythonExe)) {
    $PythonExe = "python"
}

$ScriptPath = Join-Path $ProjectDir "src\auto_produce.py"

$ArgsList = @("--audio", $Audio, "--fps", $Fps, "--lang", $Lang)
if ($Output) {
    $ArgsList += @("--output", $Output)
}
if ($PreviewOnly) {
    $ArgsList += "--preview-only"
}

Write-Host ">>> Starting Automated 2D Cinematic Documentary Production..." -ForegroundColor Cyan
& $PythonExe $ScriptPath @ArgsList
