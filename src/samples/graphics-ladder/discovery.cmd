@echo off
if "%~2"=="" goto usage
if exist "%~2.exit" goto exists
if exist "%~2.txt" goto exists
if exist "%~2-caps.bin" goto exists
"%~dp0discovery.exe" %1 "%~2"
set "XWN_RESULT=%ERRORLEVEL%"
>"%~2.exit" echo %XWN_RESULT%
exit /b %XWN_RESULT%
:exists
echo Choose a fresh output prefix.
exit /b 3
:usage
echo Usage: discovery.cmd default^|hel output-prefix
exit /b 2
