@echo off
rem SPDX-License-Identifier: MIT
rem Fresh prefix required. This wrapper has no process watchdog.
setlocal
if "%~2"=="" goto usage
if not "%~3"=="" goto usage
for %%s in (.txt .exit -source.bin -dest.bin) do if exist "%~2%%s" goto exists
"%~dp0keyprobe.exe" "%~1" "%~2"
set sample_result=%ERRORLEVEL%
> "%~2.exit" echo %sample_result%
echo Sample exit: %sample_result%. Keep all reports, including failures.
exit /b %sample_result%
:exists
echo Refused: choose a fresh result prefix.
exit /b 2
:usage
echo Usage: keyprobe.cmd default^|hel fresh-prefix
exit /b 2
