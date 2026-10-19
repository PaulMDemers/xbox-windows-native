"""MIT. Fresh source namespace after569; no closed disk reused."""
from pathlib import Path
K=Path(__file__).resolve().parent;old=K.parent/'rct569'
names=['runner.c','input.h','media001.py','review_media001.py','prepare002.py','vm.py','cold002.py','login001.py','collect001.py','review001.py','capture_review001.py','edition.json','.gitattributes']
for name in names+['build001.py']:
    dest=K/name;assert not dest.exists()
    source=old/('build002.py' if name=='build001.py' else name)
    s=source.read_text(encoding='utf-8').replace('569','570').replace('runner-build002','runner-build001')
    if name=='media001.py':s=s.replace('RUN570.EXE /pc800','RUN570.EXE')
    if name=='capture_review001.py':s=s.replace('.getdata()', '.get_flattened_data()')
    if name=='runner.c':
        s=s.replace(' if(!pcdisplay()){number("pc_display_failed",1);goto end;}\n','')
        s=s.replace(' if(displaychanged)number("pc_display_restore",ChangeDisplaySettingsA(&originalmode,0));\n','')
        s=s.replace(' zero(&si,sizeof(si));zero(&pi,sizeof(pi));si.cb=sizeof(si);',' if(GetConsoleWindow())ShowWindow(GetConsoleWindow(),SW_MINIMIZE);\n Sleep(1000);\n zero(&si,sizeof(si));zero(&pi,sizeof(pi));si.cb=sizeof(si);')
        s=s.replace('GetTickCount()-start<180000','GetTickCount()-start<300000')
    if name=='input.h':
        s=s.replace('static DEVMODEA originalmode;\nstatic BOOL displaychanged;\n','')
        s=s[:s.index('static BOOL pcdisplay(void)')]
    dest.write_bytes(s.encode())
