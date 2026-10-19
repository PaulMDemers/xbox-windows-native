@echo off
if "%~2"=="" goto usage
if exist "%~2.exit" goto exists
if exist "%~2.txt" goto exists
if exist "%~2-clear.bin" goto exists
if exist "%~2-draw.bin" goto exists
if exist "%~2-source-before.bin" goto exists
if exist "%~2-source-after.bin" goto exists
if exist "%~2-screen-before.bin" goto exists
if exist "%~2-screen-after.bin" goto exists
if exist "%~2-post.bin" goto exists
if exist "%~2-native-before.bin" goto exists
if exist "%~2-native-after.bin" goto exists
"%~dp0scenepresent.exe" %1 "%~2"
set "XWN_RESULT=%ERRORLEVEL%"
>"%~2.exit" echo %XWN_RESULT%
exit /b %XWN_RESULT%
:exists
echo Choose a fresh output prefix.
exit /b 3
:usage
echo Usage: scenepresent.cmd default^|hel output-prefix
echo Run graphics_scenepresent.py on the captures; process success alone is not pixel validation.
exit /b 2
