@echo off
cd /d C:\xwndemo387control001
if exist file-trace.log exit
echo BEGIN>file-trace.log
C:\xwndemo387control001\file-probe.exe
set XWN_FILE_RC=%ERRORLEVEL%
>>file-trace.log echo FILE_API_EXIT %XWN_FILE_RC%
>>file-trace.log echo RUNNER_START
C:\xwndemo387control001\runner.exe /physical
set XWN_RUNNER_RC=%ERRORLEVEL%
>>file-trace.log echo RUNNER_RETURN %XWN_RUNNER_RC%
exit
