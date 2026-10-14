@echo off
C:\winnt\system32\cmd.exe /d /c C:\xwncmd393\commands.cmd
cd /d C:\xwnenumeration391
if exist file-trace.log exit
echo BEGIN>file-trace.log
C:\xwnenumeration391\file-probe.exe
set XWN_FILE_RC=%ERRORLEVEL%
>>file-trace.log echo FILE_API_EXIT %XWN_FILE_RC%
>>file-trace.log echo RUNNER_START
C:\xwnenumeration391\runner.exe /emulator
set XWN_RUNNER_RC=%ERRORLEVEL%
>>file-trace.log echo RUNNER_RETURN %XWN_RUNNER_RC%
exit
