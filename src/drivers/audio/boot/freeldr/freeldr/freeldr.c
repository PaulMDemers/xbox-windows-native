/*
 *  FreeLoader
 *  Copyright (C) 1998-2003  Brian Palmer  <brianp@sginet.com>
 *
 *  This program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License along
 *  with this program; if not, write to the Free Software Foundation, Inc.,
 *  51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
 */

/* INCLUDES *******************************************************************/

#include <freeldr.h>

#include <debug.h>
#ifdef XBOX_NATIVE_IO_PREFLIGHT
#include <xwnprobe.h>
#endif
DBG_DEFAULT_CHANNEL(WARNING);

/* GLOBALS ********************************************************************/

CCHAR FrLdrBootPath[MAX_PATH] = "";

/* FUNCTIONS ******************************************************************/

#ifndef SARCH_APPLETV
static
BOOLEAN
LoadRosload(
    _In_ PCSTR RosloadPath,
    _Out_ PVOID* ImageBase,
    _Out_ PLDR_DATA_TABLE_ENTRY* DataTableEntry)
{
    CHAR FullPath[MAX_PATH];
    BOOLEAN Success;

    /* Create full rosload.exe path */
    RtlStringCbPrintfA(FullPath,
                       sizeof(FullPath),
                       "%s\\%s",
                       FrLdrBootPath,
                       RosloadPath);

    TRACE("Loading second stage loader '%s'\n", FullPath);

    /* Load rosload.exe as a bootloader image. The base name is "scsiport.sys",
       because it exports ScsiPort* functions for ntbootdd.sys */
    Success = PeLdrLoadBootImage(FullPath,
                                 "scsiport.sys",
                                 ImageBase,
                                 DataTableEntry);
    if (!Success)
    {
        WARN("Failed to load second stage loader '%s'\n", FullPath);
        return FALSE;
    }

    return TRUE;
}

static
ULONG
LaunchSecondStageLoader(VOID)
{
    PLDR_DATA_TABLE_ENTRY RosloadDTE;
    PVOID ImageBase;
    LONG (*EntryPoint)(VOID);

    /* Load the second stage loader */
    if (!LoadRosload("rosload.exe", &ImageBase, &RosloadDTE))
    {
        /* Try in loader directory */
        if (!LoadRosload("loader\\rosload.exe", &ImageBase, &RosloadDTE))
        {
            return ENOENT;
        }
    }

    /* Call the entrypoint */
    printf("Launching rosload.exe...\n");
    EntryPoint = VaToPa(RosloadDTE->EntryPoint);
    (*EntryPoint)();
    return ESUCCESS;
}

#endif

VOID __cdecl BootMain(IN PCCH CmdLine)
{
    /* Load the default settings from the command-line */
    LoadSettings(CmdLine);

    /* Debugger pre-initialization */
    DebugInit(BootMgrInfo.DebugString);

    MachInit(CmdLine);

    TRACE("BootMain() called.\n");
#if defined(XBOX_NATIVE_PREFLIGHT) || defined(XBOX_NATIVE_IO_PREFLIGHT)
    printf("XWN10: Xbox platform initialized\n");
#endif


#ifndef UEFIBOOT
    /* Check if the CPU is new enough */
    FrLdrCheckCpuCompatibility(); // FIXME: Should be done inside MachInit!
#endif

    /* UI pre-initialization */
    if (!UiInitialize(FALSE))
    {
        UiMessageBoxCritical("Unable to initialize UI.");
        goto Quit;
    }

    /* Initialize memory manager */
    if (!MmInitializeMemoryManager())
    {
        UiMessageBoxCritical("Unable to initialize memory manager.");
        goto Quit;
    }

#if defined(XBOX_NATIVE_PREFLIGHT) || defined(XBOX_NATIVE_IO_PREFLIGHT)
    printf("XWN20: Memory manager initialized\n");
#endif

    /* Initialize I/O subsystem */
    FsInit();

    /* Initialize the module list */
    if (!PeLdrInitializeModuleList())
    {
        UiMessageBoxCritical("Unable to initialize module list.");
        goto Quit;
    }

    if (!MachInitializeBootDevices())
    {
        UiMessageBoxCritical("Error when detecting hardware.");
        goto Quit;
    }
    
#ifndef SARCH_APPLETV
#ifdef XBOX_NATIVE_PREFLIGHT
    {
        PFREELDR_MEMORY_DESCRIPTOR Map;
        ULONG Count = MmGetBiosMemoryMap(&Map);
        ULONG Index;
        printf("XWN30: Boot devices initialized; path=%s\n", FrLdrBootPath);
        printf("Firmware descriptors (page units): %lu\n", Count);
        for (Index = 0; Index < Count; ++Index)
        {
            printf("%02lu base=%08lx pages=%08lx type=%lu\n",
                   Index, (ULONG)Map[Index].BasePage,
                   (ULONG)Map[Index].PageCount, (ULONG)Map[Index].MemoryType);
        }
        printf("XWN40: Diagnostic complete. Windows NOT entered.\n");
        _disable();
        for (;;) __halt();
    }
#endif

#ifdef XBOX_NATIVE_IO_PREFLIGHT
    printf("XWN30: Boot path=%s\n", FrLdrBootPath);
    if (!XwnVerifyFile()) XwnStop("XWNFAIL: first-stage file verification");
    printf("XWN50: 131075 bytes, EOF and cross-sector seek verified\n");
#endif
    /* Launch second stage loader */
    if (LaunchSecondStageLoader() != ESUCCESS)
    {
        UiMessageBoxCritical("Unable to load second stage loader.");
    }
#else
    /* We don't use rosload on Apple TV */
    RunLoader();
#endif

Quit:
    /* If we reach this point, something went wrong before, therefore reboot */
    Reboot();
}

// We need to emulate these, because the original ones don't work in freeldr
// These functions are here, because they need to be in the main compilation unit
// and cannot be in a library.
int __cdecl wctomb(char *mbchar, wchar_t wchar)
{
    *mbchar = (char)wchar;
    return 1;
}

int __cdecl mbtowc(wchar_t *wchar, const char *mbchar, size_t count)
{
    *wchar = (wchar_t)*mbchar;
    return 1;
}

// The wctype table is 144 KB, too much for poor freeldr
int __cdecl iswctype(wint_t wc, wctype_t wctypeFlags)
{
    return _isctype((char)wc, wctypeFlags);
}

#ifdef _MSC_VER
#pragma warning(disable:4164)
#pragma function(pow)
#pragma function(log)
#pragma function(log10)
#endif

// Stubs to avoid pulling in data from CRT
double pow(double x, double y)
{
    __debugbreak();
    return 0.0;
}

double log(double x)
{
    __debugbreak();
    return 0.0;
}

double log10(double x)
{
    __debugbreak();
    return 0.0;
}

PCCHAR FrLdrGetBootPath(VOID)
{
    return FrLdrBootPath;
}

UCHAR FrldrGetBootDrive(VOID)
{
    return FrldrBootDrive;
}

ULONG FrldrGetBootPartition(VOID)
{
    return FrldrBootPartition;
}
