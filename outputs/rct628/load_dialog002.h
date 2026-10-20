/* MIT. One native Open submission to the owned RCT Load Game dialog. */
static HWND loaddialog,loadedit,loadbutton;
static DWORD loaddialogcount,loadeditcount;
static const char loadpath[]="C:\\xwn628-kit\\game\\Saved Games\\XWN593.SV4";
static BOOL loadcontrol(HWND w,const char *cls,int id){
 DWORD pid=0;char c[80];zero(c,sizeof(c));GetWindowThreadProcessId(w,&pid);GetClassNameA(w,c,sizeof(c));
 return IsWindow(w)&&pid==gamepid&&IsWindowVisible(w)&&IsWindowEnabled(w)&&!lstrcmpA(c,cls)&&(id<0||GetDlgCtrlID(w)==id);
}
static BOOL CALLBACK findload(HWND w,LPARAM unused){
 char title[80];(void)unused;zero(title,sizeof(title));GetWindowTextA(w,title,sizeof(title));
 if(loadcontrol(w,"#32770",-1)&&!lstrcmpA(title,"Load Game")){loaddialog=w;loaddialogcount++;}return TRUE;
}
static BOOL CALLBACK findloadedit(HWND w,LPARAM unused){
 (void)unused;if(loadcontrol(w,"Edit",1148)&&loadcontrol(GetParent(w),"ComboBox",1148)&&
 loadcontrol(GetParent(GetParent(w)),"ComboBoxEx32",1148)&&IsChild(loaddialog,w)){loadedit=w;loadeditcount++;}return TRUE;
}
static BOOL loadidentity(void){
 char t[80],label[80];zero(t,sizeof(t));zero(label,sizeof(label));GetWindowTextA(loaddialog,t,sizeof(t));GetWindowTextA(loadbutton,label,sizeof(label));
 return loaddialogcount==1&&loadeditcount==1&&GetForegroundWindow()==loaddialog&&
 loadcontrol(loaddialog,"#32770",-1)&&!lstrcmpA(t,"Load Game")&&
 loadcontrol(loadedit,"Edit",1148)&&IsChild(loaddialog,loadedit)&&
 loadcontrol(GetParent(loadedit),"ComboBox",1148)&&loadcontrol(GetParent(GetParent(loadedit)),"ComboBoxEx32",1148)&&
 loadcontrol(loadbutton,"Button",1)&&GetParent(loadbutton)==loaddialog&&(!lstrcmpA(label,"&Open")||!lstrcmpA(label,"Open"));
}
static BOOL load_owned_park(void){
 DWORD start=GetTickCount(),high=0,size;DWORD_PTR result=0;HANDLE f;char got[MAX_PATH];BOOL posted;
 f=CreateFileA(loadpath,GENERIC_READ,FILE_SHARE_READ,0,OPEN_EXISTING,0,0);
 if(f==INVALID_HANDLE_VALUE)return FALSE;
 size=GetFileSize(f,&high);CloseHandle(f);
 number("load_file_bytes",size);if(high||size!=290244)return FALSE;
 do{loaddialog=0;loaddialogcount=0;EnumWindows(findload,0);if(loaddialogcount==1)break;Sleep(100);}while(GetTickCount()-start<10000);
 number("load_dialog_count",loaddialogcount);if(loaddialogcount!=1)return FALSE;
 loadedit=0;loadeditcount=0;EnumChildWindows(loaddialog,findloadedit,0);loadbutton=GetDlgItem(loaddialog,1);
 number("load_edit_count",loadeditcount);if(!loadidentity()){number("load_identity_failed",1);return FALSE;}
 if(!SendMessageTimeoutA(loadedit,WM_SETTEXT,0,(LPARAM)loadpath,SMTO_ABORTIFHUNG|SMTO_BLOCK,2000,&result)||!result)return FALSE;
 zero(got,sizeof(got));result=0;
 if(!SendMessageTimeoutA(loadedit,WM_GETTEXT,sizeof(got),(LPARAM)got,SMTO_ABORTIFHUNG|SMTO_BLOCK,2000,&result)||
 result!=sizeof(loadpath)-1||lstrcmpA(got,loadpath)||!loadidentity())return FALSE;
 number("load_path_readback",1);posted=PostMessageA(loadbutton,BM_CLICK,0,0);number("load_click_posted",posted);if(!posted)return FALSE;
 start=GetTickCount();while(IsWindow(loaddialog)&&GetTickCount()-start<30000)Sleep(100);
 number("load_dialog_gone",!IsWindow(loaddialog));if(IsWindow(loaddialog))return FALSE;
 Sleep(10000);return reacquire("after-load"); /* Pixel comparison, not this return, establishes the loaded scene. */
}
