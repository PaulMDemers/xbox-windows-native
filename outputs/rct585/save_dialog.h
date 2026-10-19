/* SPDX-License-Identifier: MIT. Owned NT5 Save dialog, one submission only. */
static HWND savedialog,filenameedit,savebutton;
static DWORD dialogcount,editcount;
static const char savefolder[]="C:\\xwn585-kit\\game\\Saved Games";
static const char savepath[]="C:\\xwn585-kit\\game\\Saved Games\\XWN585.SV4";
static BOOL owned_control(HWND w,const char*cls,int id){
 DWORD pid=0;char c[80];zero(c,sizeof(c));
 GetWindowThreadProcessId(w,&pid);GetClassNameA(w,c,sizeof(c));
 return IsWindow(w)&&pid==gamepid&&IsWindowVisible(w)&&IsWindowEnabled(w)&&lstrcmpA(c,cls)==0&&(id<0||GetDlgCtrlID(w)==id);
}
static BOOL CALLBACK find_save_edit(HWND w,LPARAM unused){
 HWND parent=GetParent(w),grand=GetParent(parent);(void)unused;
 if(owned_control(w,"Edit",1148)&&owned_control(parent,"ComboBox",1148)&&owned_control(grand,"ComboBoxEx32",1148)&&IsChild(savedialog,w)){filenameedit=w;editcount++;}
 return TRUE;
}
static BOOL CALLBACK find_save_dialog(HWND w,LPARAM unused){
 char title[80];(void)unused;zero(title,sizeof(title));GetWindowTextA(w,title,sizeof(title));
 if(owned_control(w,"#32770",-1)&&lstrcmpA(title,"Save Game")==0){savedialog=w;dialogcount++;}return TRUE;
}
static BOOL save_identity(void){
 char title[80];zero(title,sizeof(title));GetWindowTextA(savedialog,title,sizeof(title));
 return dialogcount==1&&editcount==1&&GetForegroundWindow()==savedialog&&
 owned_control(savedialog,"#32770",-1)&&lstrcmpA(title,"Save Game")==0&&
 owned_control(filenameedit,"Edit",1148)&&IsChild(savedialog,filenameedit)&&
 owned_control(GetParent(filenameedit),"ComboBox",1148)&&
 owned_control(GetParent(GetParent(filenameedit)),"ComboBoxEx32",1148)&&
 owned_control(savebutton,"Button",1)&&GetParent(savebutton)==savedialog;
}
static BOOL exact_save_text(void){
 char got[MAX_PATH];DWORD_PTR result=0;LRESULT sent;
 zero(got,sizeof(got));if(!save_identity())return FALSE;
 SetLastError(0);sent=SendMessageTimeoutA(filenameedit,WM_GETTEXT,sizeof(got),(LPARAM)got,SMTO_ABORTIFHUNG|SMTO_BLOCK,2000,&result);
 number("filename_gettext_completed",sent!=0);number("filename_gettext_length",(DWORD)result);number("filename_gettext_error",GetLastError());
 return sent&&result==(DWORD_PTR)lstrlenA(savepath)&&lstrcmpA(got,savepath)==0;
}
static BOOL save_owned_park(void){
 DWORD start=GetTickCount(),attributes,error;DWORD_PTR result=0;char label[80];HANDLE file;DWORD size;BOOL posted;
 attributes=GetFileAttributesA(savefolder);
 if(attributes==INVALID_FILE_ATTRIBUTES){if(!CreateDirectoryA(savefolder,0)){number("save_folder_error",GetLastError());return FALSE;}}
 else if(!(attributes&FILE_ATTRIBUTE_DIRECTORY))return FALSE;
 SetLastError(0);attributes=GetFileAttributesA(savepath);error=GetLastError();
 number("save_target_absent",attributes==INVALID_FILE_ATTRIBUTES&&error==ERROR_FILE_NOT_FOUND);
 if(attributes!=INVALID_FILE_ATTRIBUTES||error!=ERROR_FILE_NOT_FOUND)return FALSE;
 do{savedialog=0;dialogcount=0;EnumWindows(find_save_dialog,0);if(dialogcount==1)break;Sleep(100);}while(GetTickCount()-start<5000);
 if(dialogcount!=1){number("save_dialog_count",dialogcount);return FALSE;}
 filenameedit=0;editcount=0;EnumChildWindows(savedialog,find_save_edit,0);savebutton=GetDlgItem(savedialog,1);
 number("save_edit_count",editcount);zero(label,sizeof(label));GetWindowTextA(savebutton,label,sizeof(label));
 if(!save_identity()||lstrcmpA(label,"&Save")!=0){number("save_identity_failed",1);return FALSE;}
 SetLastError(0);
 if(!SendMessageTimeoutA(filenameedit,WM_SETTEXT,0,(LPARAM)savepath,SMTO_ABORTIFHUNG|SMTO_BLOCK,2000,&result)||!result){number("filename_settext_error",GetLastError());return FALSE;}
 number("filename_settext_completed",1);
 if(!exact_save_text()){number("filename_readback_failed",1);return FALSE;}
 SetLastError(0);attributes=GetFileAttributesA(savepath);error=GetLastError();
 if(attributes!=INVALID_FILE_ATTRIBUTES||error!=ERROR_FILE_NOT_FOUND||!save_identity())return FALSE;
 posted=PostMessageA(savebutton,BM_CLICK,0,0);number("save_click_posted",posted);if(!posted)return FALSE;
 /* One submission. No retry after accepted or uncertain message delivery. */
 start=GetTickCount();while(IsWindow(savedialog)&&GetTickCount()-start<15000)Sleep(100);
 number("save_dialog_gone",!IsWindow(savedialog));if(IsWindow(savedialog))return FALSE;
 file=CreateFileA(savepath,GENERIC_READ,FILE_SHARE_READ,0,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,0);
 if(file==INVALID_HANDLE_VALUE){number("saved_file_open_error",GetLastError());return FALSE;}
 size=GetFileSize(file,0);CloseHandle(file);number("saved_file_bytes",size);
 number("save_phase_file_observed",size>32&&size<8*1024*1024);
 return size>32&&size<8*1024*1024&&reacquire("after-save")&&capture("park-after-save");
}
