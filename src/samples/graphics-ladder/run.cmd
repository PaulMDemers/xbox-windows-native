@echo off
rem SPDX-License-Identifier: MIT
setlocal
if "%~4"=="" goto usage
if not "%~5"=="" goto usage
if exist "%~3.txt" goto exists
if exist "%~3.exit" goto exists
if exist "%~3-source.bin" goto exists
if exist "%~3-dest.bin" goto exists
"%~dp0ladder.exe" "%~1" "%~2" "%~3" "%~4"
set sample_result=%ERRORLEVEL%
> "%~3.exit" echo %sample_result%
echo Sample exit: %sample_result%. Keep all reports, including failures.
exit /b %sample_result%
:exists
echo Refused: choose a fresh result prefix. Existing results were not changed.
exit /b 2
:usage
echo Usage: run.cmd 00^|01^|02 default^|hel^|hal fresh-prefix view^|quiet
echo 00 uses default; 02 supports default/hel only. Use 01 for HAL inventory.
exit /b 2
