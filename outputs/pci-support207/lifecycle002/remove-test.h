/* SPDX-License-Identifier: MIT -- exact SMBus leaf only; vetoes are retained. */
static BOOL exercise_remove(DEVINST instance,DWORD capabilities)
{
    DEVINST child;CONFIGRET cr;PNP_VETO_TYPE veto=PNP_VetoTypeUnknown;
    char name[MAX_PATH];HANDLE token;TOKEN_PRIVILEGES tp;BOOL ok;
    if(capabilities&CM_DEVCAP_SURPRISEREMOVALOK){text("REMOVE_HELD_SURPRISE_CAPABLE\r\n");return FALSE;}
    cr=CM_Get_Child(&child,instance,0);number("remove_child_query=",cr);
    if(cr!=CR_NO_SUCH_DEVNODE){text("REMOVE_HELD_NOT_PROVEN_LEAF\r\n");return FALSE;}
    if(!OpenProcessToken(GetCurrentProcess(),TOKEN_ADJUST_PRIVILEGES|TOKEN_QUERY,&token))return FALSE;
    tp.PrivilegeCount=1;tp.Privileges[0].Attributes=SE_PRIVILEGE_ENABLED;
    if(!LookupPrivilegeValueA(NULL,SE_LOAD_DRIVER_NAME,&tp.Privileges[0].Luid)){CloseHandle(token);return FALSE;}
    SetLastError(ERROR_SUCCESS);ok=AdjustTokenPrivileges(token,FALSE,&tp,0,NULL,NULL);
    if(GetLastError()!=ERROR_SUCCESS)ok=FALSE;
    CloseHandle(token);if(!ok)return FALSE;
    clear_bytes(name,sizeof(name));
    text("REMOVE_REQUEST_EXACT_SMBUS_LEAF\r\n");
    cr=CM_Query_And_Remove_SubTreeA(instance,&veto,name,sizeof(name),CM_REMOVE_UI_OK);
    number("remove_result=",cr);number("remove_veto=",veto);text("remove_veto_name=");text(name);text("\r\n");
    if(cr!=CR_SUCCESS)return FALSE;
    if(query()){text("REMOVE_INTERFACE_STILL_ACTIVE\r\n");return FALSE;}
    text("REMOVE_INTERFACE_ABSENT\r\n");
    text("REENUMERATE_REQUEST_EXACT_SMBUS\r\n");
    cr=CM_Reenumerate_DevNode(instance,CM_REENUMERATE_SYNCHRONOUS);number("reenumerate_result=",cr);
    if(cr!=CR_SUCCESS)return FALSE;
    Sleep(1000);return query();
}
