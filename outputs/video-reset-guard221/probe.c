#define _WIN32_WINNT 0x0500
#include <windows.h>
#include <winioctl.h>
static HANDLE Log;
static void line(const char *s)
{
    DWORD n = lstrlenA(s), written;
    if (!WriteFile(Log, s, n, &written, NULL) || written != n || !FlushFileBuffers(Log)) ExitProcess(92);
}
static void fail(const char *s) { line(s); ExitProcess(91); }
void __stdcall mainCRTStartup(void)
{
    HKEY key; DWORD type, size = 4, enabled = 0, returned;
    SC_HANDLE scm, svc; HANDLE device, volume;
    DWORD cookie[4] = {0x44554d50, 0x221, 0x10000, 1};
    Log = CreateFileA("C:\\xwnguard221\\intent.log", GENERIC_WRITE, FILE_SHARE_READ, NULL,
                      CREATE_NEW, FILE_ATTRIBUTE_NORMAL | FILE_FLAG_WRITE_THROUGH, NULL);
    if (Log == INVALID_HANDLE_VALUE) ExitProcess(90);
    line("INTENT E058D221 44554D50 00000221 00010000 00000001\r\n");
    if (RegOpenKeyExA(HKEY_LOCAL_MACHINE,"SYSTEM\\CurrentControlSet\\Control\\CrashControl",0,KEY_QUERY_VALUE,&key)) fail("FAIL REGISTRY\r\n");
    if (RegQueryValueExA(key,"CrashDumpEnabled",NULL,&type,(BYTE*)&enabled,&size) || type != REG_DWORD || size != 4 || enabled != 3) fail("FAIL DUMP_MODE\r\n");
    RegCloseKey(key);
    scm = OpenSCManagerA(NULL,NULL,SC_MANAGER_CREATE_SERVICE);
    if (!scm) fail("FAIL SCM\r\n");
    svc = CreateServiceA(scm,"XwnGuardTest221","Owned emulator one-shot dump test",SERVICE_START|SERVICE_QUERY_STATUS,
                        SERVICE_KERNEL_DRIVER,SERVICE_DEMAND_START,SERVICE_ERROR_NORMAL,
                        "C:\\xwnguard221\\trigger.sys",NULL,NULL,NULL,NULL,NULL);
    if (!svc) fail("FAIL CREATE_SERVICE\r\n");
    if (!StartServiceA(svc,0,NULL)) fail("FAIL START_SERVICE\r\n");
    CloseServiceHandle(svc); CloseServiceHandle(scm);
    device = CreateFileA("\\\\.\\XwnGuardTest221",GENERIC_WRITE,0,NULL,OPEN_EXISTING,0,NULL);
    if (device == INVALID_HANDLE_VALUE) fail("FAIL OPEN_DEVICE\r\n");
    line("DRIVER_READY; WAITING_90000_MS\r\n");
    Sleep(90000);
    line("TRIGGER_ONCE\r\n");
    volume = CreateFileA("\\\\.\\C:",GENERIC_READ|GENERIC_WRITE,FILE_SHARE_READ|FILE_SHARE_WRITE,NULL,OPEN_EXISTING,0,NULL);
    if (volume == INVALID_HANDLE_VALUE) fail("FAIL OPEN_VOLUME\r\n");
    if (!FlushFileBuffers(volume)) fail("FAIL FLUSH_VOLUME\r\n");
    CloseHandle(volume);
    Sleep(5000);
    DeviceIoControl(device,CTL_CODE(FILE_DEVICE_UNKNOWN,0x803,METHOD_BUFFERED,FILE_WRITE_ACCESS),cookie,sizeof(cookie),NULL,0,&returned,NULL);
    fail("FAIL TRIGGER_RETURNED\r\n");
}
