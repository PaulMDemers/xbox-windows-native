"""MIT. New foreground-preserving helper; no closed runtime reused."""
from pathlib import Path
K=Path(__file__).resolve().parent;old=K.parent/'rct570'
names=['runner.c','input.h','title_signature.h','build001.py','media001.py','review_media001.py','prepare002.py','vm.py','cold002.py','login001.py','collect001.py','review001.py','capture_review001.py','edition.json','.gitattributes']
for name in names:
    dest=K/name;assert not dest.exists()
    s=(old/name).read_text(encoding='utf-8').replace('570','571')
    if name=='runner.c':
        s=s.replace(' if(GetConsoleWindow())ShowWindow(GetConsoleWindow(),SW_MINIMIZE);\n Sleep(1000);\n','')
        s=s.replace('DWORD pd=0,kd=0,language=0,code=99,start,wait=WAIT_FAILED;', 'DWORD pd=0,kd=0,language=0,code=99,wait=WAIT_FAILED;')
        s=s.replace('gamepid=pi.dwProcessId;number("game_pid",gamepid);start=GetTickCount();','gamepid=pi.dwProcessId;number("game_pid",gamepid);')
        begin=s.index(' do{wait=WaitForSingleObject(pi.hProcess,5000);')
        end=s.index(' number("wait",wait);',begin)
        s=s[:begin]+' modules();EnumWindows(windows,0);wait=WaitForSingleObject(pi.hProcess,0);\n'+s[end:]
        s=s.replace(' CloseHandle(pi.hProcess);', ' CloseHandle(pi.hProcess);number("desktop_restored",GetSystemMetrics(SM_CXSCREEN)==initialwidth&&GetSystemMetrics(SM_CYSCREEN)==initialheight);')
        s=s.replace(' number("schema",571);number("start_tick",GetTickCount());',' number("schema",571);number("start_tick",GetTickCount());\n initialwidth=GetSystemMetrics(SM_CXSCREEN);initialheight=GetSystemMetrics(SM_CYSCREEN);number("initial_width",initialwidth);number("initial_height",initialheight);')
    dest.write_bytes(s.encode())
