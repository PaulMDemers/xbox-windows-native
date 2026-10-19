"""Prepare a new PC-only Save Game dialog inspection; no saved runtime reuse."""
from pathlib import Path
K=Path(__file__).resolve().parent;old=K.parent/'rct575'
for name in ['runner.c','input.h','game_capture.h','title_signature.h','build001.py','media001.py','review_media001.py','prepare002.py','vm.py','cold002.py','login001.py','collect001.py','review001.py','edition.json','.gitattributes']:
 dest=K/name;assert not dest.exists()
 dest.write_bytes((old/name).read_text().replace('575','578').encode())
p=K/'input.h';s=p.read_text()
start=s.index('static BOOL relative(');end=s.index('static void releaseinputs',start);s=s[:start]+s[end:]
start=s.index('static BOOL keyhold(');end=s.index('static BOOL gamecapture',start);s=s[:start]+s[end:]
start=s.index('static BOOL scrollcases(');end=s.index('static BOOL options(',start);s=s[:start]+s[end:]
start=s.index(' if(!scrollcases(');s=s[:start]+''' if(!capture("park-before-save")||!click(44,14)||!capture("save-menu")||!click(76,50))return FALSE;
 Sleep(5000);number("save_dialog_inspection_tick",GetTickCount());
 EnumWindows(inspect_top,0);Sleep(10000);
 if(!cancel_owned_dialog())return FALSE;
 Sleep(2000);return reacquire("after-save-cancel")&&capture("park-after-cancel");
}
'''
new='''static BOOL CALLBACK inspect_child(HWND w,LPARAM unused){
 DWORD pid=0;char cls[80],title[160],line[512];RECT r;(void)unused;
 GetWindowThreadProcessId(w,&pid);if(pid!=gamepid)return TRUE;
 zero(&r,sizeof(r));zero(cls,sizeof(cls));zero(title,sizeof(title));
 GetClassNameA(w,cls,sizeof(cls));GetWindowTextA(w,title,sizeof(title));GetWindowRect(w,&r);
 wsprintfA(line,"dialog_control hwnd=%lu id=%d class=%s visible=%lu enabled=%lu rect=%ld,%ld,%ld,%ld text=%s\\r\\n",(DWORD)w,GetDlgCtrlID(w),cls,(DWORD)IsWindowVisible(w),(DWORD)IsWindowEnabled(w),r.left,r.top,r.right,r.bottom,title);
 bytes(logh,line,lstrlenA(line));return TRUE;
}
static BOOL CALLBACK inspect_top(HWND w,LPARAM unused){
 DWORD pid=0;(void)unused;GetWindowThreadProcessId(w,&pid);
 if(pid==gamepid&&IsWindowVisible(w)){inspect_child(w,0);EnumChildWindows(w,inspect_child,0);}return TRUE;
}
static BOOL cancel_owned_dialog(void){
 DWORD pid=0;HWND w=GetForegroundWindow();INPUT i;BOOL down,up;char cls[80];
 zero(cls,sizeof(cls));GetWindowThreadProcessId(w,&pid);GetClassNameA(w,cls,sizeof(cls));
 if(pid!=gamepid||!IsWindowVisible(w)||(w!=gamewindow&&lstrcmpA(cls,"#32770")!=0)){number("dialog_cancel_identity_failed",1);return FALSE;}
 keyevent(&i,VK_ESCAPE,FALSE);down=SendInput(1,&i,sizeof(i))==1;Sleep(120);
 keyevent(&i,VK_ESCAPE,TRUE);up=SendInput(1,&i,sizeof(i))==1;
 number("dialog_cancel_submitted",down&&up);return down&&up;
}
'''
s=s.replace('static BOOL runinputs(void){',new+'static BOOL runinputs(void){')
p.write_bytes(s.encode())
