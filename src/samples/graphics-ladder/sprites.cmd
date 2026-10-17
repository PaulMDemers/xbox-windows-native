@echo off
rem SPDX-License-Identifier: MIT
setlocal
if "%~3"=="" goto usage
if not "%~4"=="" goto usage
for %%s in (.txt .exit -source.bin -dest.bin -rgb.bin -palette.bin) do if exist "%~3%%s" goto exists
"%~dp0sprites.exe" "%~1" "%~2" "%~3"
set sample_result=%ERRORLEVEL%
> "%~3.exit" echo %sample_result%
echo Sample exit: %sample_result%. Keep all reports, including failures.
exit /b %sample_result%
:exists
echo Refused: choose a fresh result prefix.
exit /b 2
:usage
echo Usage: sprites.cmd default^|hel index8^|rgb565^|rgb32 fresh-prefix
exit /b 2
