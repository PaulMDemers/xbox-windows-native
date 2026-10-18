@echo off
rem SPDX-License-Identifier: MIT
setlocal
if "%~2"=="" goto usage
if not "%~3"=="" goto usage
for %%s in (.txt .exit -source.bin -before.bin -after.bin -post.bin) do if exist "%~2%%s" goto exists
"%~dp0d3dpresent.exe" "%~1" "%~2"
set sample_result=%ERRORLEVEL%
> "%~2.exit" echo %sample_result%
echo Sample exit: %sample_result%. Keep all reports, including failures.
exit /b %sample_result%
:exists
echo Refused: choose a fresh result prefix. Existing results were not changed.
exit /b 2
:usage
echo Usage: d3dpresent.cmd default^|hel fresh-prefix
echo Requires a visible unobstructed desktop. No display-mode change.
exit /b 2
