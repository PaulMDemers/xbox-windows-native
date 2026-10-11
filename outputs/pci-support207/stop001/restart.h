static void guarded_restart(void)
{
    typedef DWORD (WINAPI *wait_install)(DWORD);
    wait_install wait;HANDLE token;TOKEN_PRIVILEGES tp;DWORD state,start,idle=0;
    BOOL have_idle=FALSE,ok;
    wait=(wait_install)GetProcAddress(LoadLibraryA("setupapi.dll"),"CMP_WaitNoPendingInstallEvents");
    if(!wait){number("setup_lookup_error=",GetLastError());ExitProcess(31);}
    /* Require five continuous seconds idle, bounded by thirty seconds. */
    start=GetTickCount();
    for(;;) {
        state=wait(0);
        if(state!=WAIT_OBJECT_0 && state!=WAIT_TIMEOUT){number("setup_query_failure=",state);ExitProcess(32);}
        if(state==WAIT_OBJECT_0) {
            if(!have_idle){idle=GetTickCount();have_idle=TRUE;}
            if(GetTickCount()-idle>=5000)break;
        } else have_idle=FALSE;
        if(GetTickCount()-start>=30000){number("restart_blocked_pending_install=",state);ExitProcess(33);}
        Sleep(250);
    }
    if(!OpenProcessToken(GetCurrentProcess(),TOKEN_ADJUST_PRIVILEGES|TOKEN_QUERY,&token))ExitProcess(34);
    tp.PrivilegeCount=1;tp.Privileges[0].Attributes=SE_PRIVILEGE_ENABLED;
    if(!LookupPrivilegeValueA(NULL,SE_SHUTDOWN_NAME,&tp.Privileges[0].Luid))ExitProcess(35);
    SetLastError(ERROR_SUCCESS);
    if(!AdjustTokenPrivileges(token,FALSE,&tp,0,NULL,NULL)||GetLastError()!=ERROR_SUCCESS)ExitProcess(36);
    CloseHandle(token);
    state=wait(0);number("pre_restart_install_state=",state);
    if(state!=WAIT_OBJECT_0){number("restart_blocked_recheck=",state);ExitProcess(37);}
    text("normal_restart_request\r\n");ok=ExitWindowsEx(EWX_REBOOT,0);
    number("normal_restart_accepted=",ok);if(!ok)number("restart_error=",GetLastError());
}
