@echo off
cd /d C:\xwndemo385control001
if exist file-trace.log exit
echo BEGIN>file-trace.log
if exist file-complete.txt goto stale
if exist saved.bmp goto stale
if exist reopened.bmp goto stale
if exist saved.tmp goto stale
if exist note.tmp goto stale
if exist note.txt goto stale
if exist note-reopened.txt goto stale
echo BEFORE COPY_BMP ERRORLEVEL=%ERRORLEVEL%>>file-trace.log
copy /b input.bmp saved.tmp >>files.log 2>&1
set XWN_RC=%ERRORLEVEL%
echo RC COPY_BMP %XWN_RC%>>file-trace.log
if not "%XWN_RC%"=="0" goto file_failed
echo BEFORE MOVE_BMP ERRORLEVEL=%ERRORLEVEL%>>file-trace.log
move saved.tmp saved.bmp >>files.log 2>&1
set XWN_RC=%ERRORLEVEL%
echo RC MOVE_BMP %XWN_RC%>>file-trace.log
if not "%XWN_RC%"=="0" goto file_failed
echo BEFORE REOPEN_BMP ERRORLEVEL=%ERRORLEVEL%>>file-trace.log
copy /b saved.bmp reopened.bmp >>files.log 2>&1
set XWN_RC=%ERRORLEVEL%
echo RC REOPEN_BMP %XWN_RC%>>file-trace.log
if not "%XWN_RC%"=="0" goto file_failed
echo BEFORE WRITE_NOTE ERRORLEVEL=%ERRORLEVEL%>>file-trace.log
echo XWN385 text persistence check>note.tmp 2>>files.log
set XWN_RC=%ERRORLEVEL%
echo RC WRITE_NOTE %XWN_RC%>>file-trace.log
if not "%XWN_RC%"=="0" goto file_failed
echo BEFORE MOVE_NOTE ERRORLEVEL=%ERRORLEVEL%>>file-trace.log
move note.tmp note.txt >>files.log 2>&1
set XWN_RC=%ERRORLEVEL%
echo RC MOVE_NOTE %XWN_RC%>>file-trace.log
if not "%XWN_RC%"=="0" goto file_failed
echo BEFORE REOPEN_NOTE ERRORLEVEL=%ERRORLEVEL%>>file-trace.log
copy /b note.txt note-reopened.txt >>files.log 2>&1
set XWN_RC=%ERRORLEVEL%
echo RC REOPEN_NOTE %XWN_RC%>>file-trace.log
if not "%XWN_RC%"=="0" goto file_failed
echo COMPLETE>file-complete.txt
echo FILE_SUCCESS>>file-trace.log
goto run
:file_failed
echo FILE_FAILED>>file-trace.log
goto run
:stale
echo STALE_REFUSAL>>file-trace.log
exit
:run
echo RUNNER_START>>file-trace.log
C:\xwndemo385control001\runner.exe /physical
set XWN_RUNNER_RC=%ERRORLEVEL%
echo RUNNER_RETURN %XWN_RUNNER_RC%>>file-trace.log
exit
