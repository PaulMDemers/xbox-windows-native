@echo off
cd /d C:\xwndemo398candidate001\cmd
if exist file-trace.log exit
echo BEGIN>file-trace.log
if exist file-complete.txt goto stale
if exist saved.bmp goto stale
if exist reopened.bmp goto stale
if exist saved.tmp goto stale
if exist note.tmp goto stale
if exist note.txt goto stale
if exist note-reopened.txt goto stale
>>file-trace.log echo BEFORE COPY_BMP ERRORLEVEL=%ERRORLEVEL%
copy /b input.bmp saved.tmp >>files.log 2>&1
set XWN_RC=%ERRORLEVEL%
>>file-trace.log echo RC COPY_BMP %XWN_RC%
if not "%XWN_RC%"=="0" goto file_failed
>>file-trace.log echo BEFORE MOVE_BMP ERRORLEVEL=%ERRORLEVEL%
move saved.tmp saved.bmp >>files.log 2>&1
set XWN_RC=%ERRORLEVEL%
>>file-trace.log echo RC MOVE_BMP %XWN_RC%
if not "%XWN_RC%"=="0" goto file_failed
>>file-trace.log echo BEFORE REOPEN_BMP ERRORLEVEL=%ERRORLEVEL%
copy /b saved.bmp reopened.bmp >>files.log 2>&1
set XWN_RC=%ERRORLEVEL%
>>file-trace.log echo RC REOPEN_BMP %XWN_RC%
if not "%XWN_RC%"=="0" goto file_failed
>>file-trace.log echo BEFORE WRITE_NOTE ERRORLEVEL=%ERRORLEVEL%
echo XWN385 text persistence check>note.tmp 2>>files.log
set XWN_RC=%ERRORLEVEL%
>>file-trace.log echo RC WRITE_NOTE %XWN_RC%
if not "%XWN_RC%"=="0" goto file_failed
>>file-trace.log echo BEFORE MOVE_NOTE ERRORLEVEL=%ERRORLEVEL%
move note.tmp note.txt >>files.log 2>&1
set XWN_RC=%ERRORLEVEL%
>>file-trace.log echo RC MOVE_NOTE %XWN_RC%
if not "%XWN_RC%"=="0" goto file_failed
>>file-trace.log echo BEFORE REOPEN_NOTE ERRORLEVEL=%ERRORLEVEL%
copy /b note.txt note-reopened.txt >>files.log 2>&1
set XWN_RC=%ERRORLEVEL%
>>file-trace.log echo RC REOPEN_NOTE %XWN_RC%
if not "%XWN_RC%"=="0" goto file_failed
echo COMPLETE>file-complete.txt
>>file-trace.log echo FILE_SUCCESS
goto run
:file_failed
>>file-trace.log echo FILE_FAILED
goto run
:stale
>>file-trace.log echo STALE_REFUSAL
exit
:run
exit
