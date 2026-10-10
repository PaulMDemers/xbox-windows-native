@echo off
cmd /c exit 0
echo INVENTORY_EXIT %errorlevel%>bad.txt
cmd /c exit 0
>good.txt echo INVENTORY_EXIT %errorlevel%
cmd /c exit 0
>>good.txt echo OBSERVER_EXIT %errorlevel%
