@echo off
if "%~2"=="" goto usage
if exist "%~2.exit" goto exists
if exist "%~2.txt" goto exists
if exist "%~2-clear.bin" goto exists
if exist "%~2-draw.bin" goto exists
"%~dp0transform.exe" %1 "%~2"
set "XWN_RESULT=%ERRORLEVEL%"
>"%~2.exit" echo %XWN_RESULT%
exit /b %XWN_RESULT%
:exists
echo Choose a fresh output prefix.
exit /b 3
:usage
echo Usage: transform.cmd default^|hel output-prefix
echo Run graphics_transform.py on the captures; process success alone is not pixel validation.
exit /b 2
