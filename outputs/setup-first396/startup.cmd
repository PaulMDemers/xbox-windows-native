@echo off
cd /d C:\xwndemo396control001
if exist file-trace.log exit
echo BEGIN>file-trace.log
echo Settling known hardware prompts before file tests...
>>file-trace.log echo GATE_START
C:\xwndemo396control001\gate\wizard.exe /cancel-physical
set XWN_GATE_RC=%ERRORLEVEL%
>>file-trace.log echo GATE_EXIT %XWN_GATE_RC%
if not "%XWN_GATE_RC%"=="0" goto blocked
echo Running direct file API control with original storage driver...
>>file-trace.log echo FILE_API_START
C:\xwndemo396control001\file-probe.exe
set XWN_FILE_RC=%ERRORLEVEL%
>>file-trace.log echo FILE_API_EXIT %XWN_FILE_RC%
echo Running command file operations...
>>file-trace.log echo CMD_START
C:\winnt\system32\cmd.exe /d /c C:\xwndemo396control001\cmd\commands.cmd
set XWN_CMD_RC=%ERRORLEVEL%
>>file-trace.log echo CMD_EXIT %XWN_CMD_RC%
>>file-trace.log echo RUNNER_START
echo Running audio and graphics checks...
C:\xwndemo396control001\runner.exe /physical
set XWN_RUNNER_RC=%ERRORLEVEL%
>>file-trace.log echo RUNNER_RETURN %XWN_RUNNER_RC%
exit
:blocked
echo Setup did not settle. File tests have not started.
>>file-trace.log echo GATE_BLOCKED
exit
