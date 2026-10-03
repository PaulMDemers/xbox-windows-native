/* Small Win2000 user-mode installer for the private NVNET experiment. */
#define WIN32_LEAN_AND_MEAN
#define _WIN32_WINNT 0x0500
#include <windows.h>
typedef BOOL (WINAPI *UPDATE_DRIVER)(HWND, LPCSTR, LPCSTR, DWORD, PBOOL);
static HANDLE Log;
static void line(const char *text)
{
    DWORD written, size = lstrlenA(text);
    WriteFile(GetStdHandle(STD_OUTPUT_HANDLE), text, size, &written, NULL);
    if (Log != INVALID_HANDLE_VALUE) {
        WriteFile(Log, text, size, &written, NULL);
        FlushFileBuffers(Log);
    }
}
static void number(const char *name, DWORD value)
{
    char digits[16]; unsigned index = sizeof(digits);
    digits[--index] = 0; digits[--index] = '\n'; digits[--index] = '\r';
    do { digits[--index] = '0' + value % 10; value /= 10; } while (value);
    line(name); line(digits + index);
}
void WINAPI mainCRTStartup(void)
{
    HMODULE module; UPDATE_DRIVER update; BOOL reboot = FALSE, result;
    DWORD error;
    Log = CreateFileA("C:\\xwnsetup.log", GENERIC_WRITE, FILE_SHARE_READ, NULL,
                      CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    line("XWN Windows 2000 NVNET driver installation experiment\r\n");
    module = LoadLibraryA("newdev.dll");
    update = module ? (UPDATE_DRIVER)GetProcAddress(module, "UpdateDriverForPlugAndPlayDevicesA") : NULL;
    if (!update) { number("API lookup error: ", GetLastError()); ExitProcess(1); }
    line("Installing C:\\nvnetnt5.inf for PCI\\VEN_10DE&DEV_01C3.\r\n");
    Sleep(5000);
    result = update(NULL, "PCI\\VEN_10DE&DEV_01C3", "C:\\nvnetnt5.inf", 1, &reboot);
    error = result ? 0 : GetLastError();
    number("Success: ", result); number("Error: ", error); number("Reboot required: ", reboot);
    if (Log != INVALID_HANDLE_VALUE) CloseHandle(Log);
    Sleep(30000);
    ExitProcess(error);
}
