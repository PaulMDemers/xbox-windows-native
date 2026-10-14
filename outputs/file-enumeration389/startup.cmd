@echo off
cd /d C:\xwnenumeration389
if exist file-trace.log exit
echo BEGIN>file-trace.log
C:\xwnenumeration389\file-probe.exe
set XWN_FILE_RC=%ERRORLEVEL%
>>file-trace.log echo FILE_API_EXIT %XWN_FILE_RC%
>>file-trace.log echo RUNNER_START
C:\xwnenumeration389\runner.exe /emulator
set XWN_RUNNER_RC=%ERRORLEVEL%
>>file-trace.log echo RUNNER_RETURN %XWN_RUNNER_RC%
exit
