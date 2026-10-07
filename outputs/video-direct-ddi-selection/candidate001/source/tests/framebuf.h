/* Host-only API shim for the actual surface.c fault-unwind tests. */
#include <stdint.h>
#include <string.h>
#include <stddef.h>
typedef uint32_t ULONG, DWORD;
typedef int32_t LONG;
typedef int BOOL;
typedef void VOID, *PVOID, *HANDLE, *HSURF, *DHPDEV;
typedef struct { LONG cx, cy; } SIZEL;
typedef struct { PVOID RequestedVirtualAddress; } VIDEO_MEMORY;
typedef struct { PVOID VideoRamBase; ULONG VideoRamLength; PVOID FrameBufferBase; ULONG FrameBufferLength; } VIDEO_MEMORY_INFORMATION;
typedef struct { HANDLE hDriver; HANDLE hDevEng; HSURF hSurfEng; PVOID ScreenPtr; ULONG ModeIndex,ScreenWidth,ScreenHeight,ScreenDelta,BitsPerPixel,iDitherFormat; PVOID PaletteEntries; } PDEV,*PPDEV;
#define IN
#define APIENTRY
#define TRUE 1
#define FALSE 0
#define BMF_8BPP 3
#define BMF_16BPP 4
#define BMF_24BPP 5
#define BMF_32BPP 6
#define BMF_TOPDOWN 1
#define IOCTL_VIDEO_SET_CURRENT_MODE 1
#define IOCTL_VIDEO_MAP_VIDEO_MEMORY 2
#define IOCTL_VIDEO_UNMAP_VIDEO_MEMORY 3
#define IOCTL_VIDEO_RESET_DEVICE 4
#define RtlZeroMemory(p,n) memset(p,0,n)
ULONG EngDeviceIoControl(HANDLE,ULONG,PVOID,ULONG,PVOID,ULONG,ULONG*);
BOOL IntSetPalette(DHPDEV,PVOID,ULONG,ULONG);
HSURF EngCreateBitmap(SIZEL,LONG,ULONG,ULONG,PVOID);
BOOL EngAssociateSurface(HSURF,HANDLE,ULONG);
BOOL EngDeleteSurface(HSURF);
HSURF DrvEnableSurface(DHPDEV);
VOID DrvDisableSurface(DHPDEV);
BOOL DrvAssertMode(DHPDEV,BOOL);
