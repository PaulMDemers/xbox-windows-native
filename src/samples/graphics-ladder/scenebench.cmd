@echo off
if "%~2"=="" goto usage
if exist "%~2.exit" goto exists
"%~dp0scenebench.exe" %1 "%~2"
set "XWN_RESULT=%ERRORLEVEL%"
if "%XWN_RESULT%"=="2" exit /b 2
>"%~2.exit" echo %XWN_RESULT%
exit /b %XWN_RESULT%
:exists
echo Choose a fresh prefix containing only letters, digits or hyphens.
exit /b 3
:usage
echo Usage: scenebench.cmd default^|hel prefix
echo Keep scene.exe beside scenebench.exe. Run graphics_scenebench.py on all captures.
exit /b 2
