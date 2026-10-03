/* Small Win2000 user-mode installer for the private ACI MMIO experiment. */
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
    Log = CreateFileA("C:\\xwnswsetup.log", GENERIC_WRITE, FILE_SHARE_READ, NULL,
                      CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    line("XWN Windows 2000 WDM software audio installation experiment\r\n");
    module = LoadLibraryA("newdev.dll");
    update = module ? (UPDATE_DRIVER)GetProcAddress(module, "UpdateDriverForPlugAndPlayDevicesA") : NULL;
    if (!update) { number("API lookup error: ", GetLastError()); ExitProcess(1); }
    {
        const char *ids[] = {
          "SW\\{A7C7A5B0-5AF3-11D1-9CED-00A024BF0407}",
          "SW\\{B7EAFDC0-A680-11D0-96D8-00AA0051E51D}",
          "SW\\{CD171DE3-69E5-11D2-B56D-0000F8754380}"
        };
        unsigned i; DWORD failures = 0;
        Sleep(10000);
        for (i = 0; i < 3; ++i) {
            line(ids[i]); line("\r\n"); reboot = FALSE;
            result = update(NULL, ids[i], "C:\\WINNT\\inf\\wdmaudio.inf", 1, &reboot);
            error = result ? 0 : GetLastError();
            number("Success: ", result); number("Error: ", error); number("Reboot required: ", reboot);
            if (!result) ++failures;
        }
        error = failures;
    }
    if (Log != INVALID_HANDLE_VALUE) CloseHandle(Log);
    Sleep(30000);
    ExitProcess(error);
}

