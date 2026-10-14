@echo off
C:\winnt\system32\cmd.exe /d /c C:\xwndemo394candidate001\cmd\commands.cmd
cd /d C:\xwndemo394candidate001
if exist file-trace.log exit
echo BEGIN>file-trace.log
C:\xwndemo394candidate001\file-probe.exe
set XWN_FILE_RC=%ERRORLEVEL%
>>file-trace.log echo FILE_API_EXIT %XWN_FILE_RC%
>>file-trace.log echo RUNNER_START
C:\xwndemo394candidate001\runner.exe /physical
set XWN_RUNNER_RC=%ERRORLEVEL%
>>file-trace.log echo RUNNER_RETURN %XWN_RUNNER_RC%
exit
