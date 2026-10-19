"""MIT. New native input control; preserve closed572 and immutable404 parent."""
from pathlib import Path
K=Path(__file__).resolve().parent;old=K.parent/'rct572'
for name in ['runner.c','input.h','title_signature.h','build001.py','media001.py','review_media001.py','prepare002.py','vm.py','cold002.py','login001.py','collect001.py','review001.py','capture_review001.py','input_review001.py','edition.json','.gitattributes']:
    dest=K/name;assert not dest.exists()
    dest.write_bytes((old/name).read_text(encoding='utf-8').replace('572','573').encode())
p=K/'input.h';s=p.read_text()
s=s.replace('static DWORD capturecount;','static DWORD capturecount,gamewindowcount;')
s=s.replace(')==0)gamewindow=w;',')==0){gamewindow=w;gamewindowcount++;}')
assert 'gamewindowcount++;' in s
s=s.replace('static void releaseinputs(void){', '''static BOOL reacquire(const char* tag){
 DWORD started=GetTickCount();
 do{gamewindow=0;gamewindowcount=0;EnumWindows(findgame,0);
  number("owned_window_count",gamewindowcount);
  if(gamewindowcount==1&&state(tag)){number("reacquired_hwnd",(DWORD)gamewindow);return TRUE;}
  Sleep(250);
 }while(GetTickCount()-started<10000);
 number("reacquire_timeout",1);return FALSE;
}
static void keyevent(INPUT* i,WORD vk,BOOL up){
 zero(i,sizeof(*i));i->type=INPUT_KEYBOARD;i->ki.wScan=(WORD)MapVirtualKeyA(vk,0);
 i->ki.dwFlags=KEYEVENTF_SCANCODE|(vk==VK_LEFT||vk==VK_RIGHT?KEYEVENTF_EXTENDEDKEY:0)|(up?KEYEVENTF_KEYUP:0);
}
static BOOL relative(int dx,int dy){
 INPUT i;POINT p;BOOL ok;
 if(!state("relative_before")||!GetCursorPos(&p)||!ScreenToClient(gamewindow,&p)||p.x<0||p.y<0||p.x>=640||p.y>=480||!exposed(p.x,p.y))return FALSE;
 zero(&i,sizeof(i));i.type=INPUT_MOUSE;i.mi.dwFlags=MOUSEEVENTF_MOVE;i.mi.dx=dx;i.mi.dy=dy;
 ok=SendInput(1,&i,sizeof(i))==1;Sleep(100);
 return ok&&state("relative_after");
}
static void releaseinputs(void){''')
# relative calls exposed, which is defined below releaseinputs.
s=s.replace('static BOOL reacquire(', 'static BOOL exposed(int x,int y);\nstatic BOOL reacquire(',1)
s=s.replace('i[1].type=INPUT_KEYBOARD;i[1].ki.wVk=VK_RIGHT;i[1].ki.dwFlags=KEYEVENTF_KEYUP;', 'keyevent(&i[1],VK_RIGHT,TRUE);')
s=s.replace('i[2].type=INPUT_KEYBOARD;i[2].ki.wVk=VK_LEFT;i[2].ki.dwFlags=KEYEVENTF_KEYUP;', 'keyevent(&i[2],VK_LEFT,TRUE);')
s=s.replace('i[3].type=INPUT_KEYBOARD;i[3].ki.wVk=VK_ESCAPE;i[3].ki.dwFlags=KEYEVENTF_KEYUP;', 'keyevent(&i[3],VK_ESCAPE,TRUE);')
oldkey='zero(&i,sizeof(i));i.type=INPUT_KEYBOARD;i.ki.wVk=vk;down=SendInput(1,&i,sizeof(i))==1;Sleep(ms);i.ki.dwFlags=KEYEVENTF_KEYUP;up=SendInput(1,&i,sizeof(i))==1;'
newkey='keyevent(&i,vk,FALSE);number("key_scan",i.ki.wScan);number("key_flags",i.ki.dwFlags);down=SendInput(1,&i,sizeof(i))==1;Sleep(100);number("key_async_down",(DWORD)(GetAsyncKeyState(vk)&0x8000));Sleep(ms);keyevent(&i,vk,TRUE);up=SendInput(1,&i,sizeof(i))==1;'
assert oldkey in s;s=s.replace(oldkey,newkey)
s=s.replace('if(!point(320-i*10,240-i*5))','if(!relative(-10,-5))')
s=s.replace('gamewindow=0;EnumWindows(findgame,0);','gamewindow=0;gamewindowcount=0;EnumWindows(findgame,0);')
s=s.replace('if(state("ready"))break;','if(gamewindowcount==1&&state("ready"))break;')
s=s.replace('if(!capture("full-options")', 'if(!reacquire("fullscreen_reacquire")||!capture("full-options")')
s=s.replace('if(!capture("restored-options")', 'if(!reacquire("window_reacquire")||!capture("restored-options")')
p.write_bytes(s.encode())
