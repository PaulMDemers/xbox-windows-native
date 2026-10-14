@echo off
cd /d C:\xwndemo382control001
if exist file-complete.txt exit
if exist saved.bmp exit
if exist reopened.bmp exit
if exist saved.tmp exit
if exist note.tmp exit
if exist note.txt exit
if exist note-reopened.txt exit
copy /b input.bmp saved.tmp > files.log
if errorlevel 1 exit
move saved.tmp saved.bmp >> files.log
if errorlevel 1 exit
copy /b saved.bmp reopened.bmp >> files.log
if errorlevel 1 exit
echo XWN382 text persistence check>note.tmp
move note.tmp note.txt >> files.log
if errorlevel 1 exit
copy /b note.txt note-reopened.txt >> files.log
if errorlevel 1 exit
echo COMPLETE>file-complete.txt
C:\xwndemo382control001\runner.exe /physical
exit
