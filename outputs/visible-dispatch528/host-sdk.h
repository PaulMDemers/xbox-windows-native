/* SPDX-License-Identifier: MIT; MODEL declarations only, never Xbox build inputs. */
#include <stdint.h>
#include <stddef.h>
typedef int BOOL;
typedef uint32_t DWORD,ULONG;
typedef int32_t NTSTATUS;
typedef void *HANDLE;
typedef struct {char *Buffer;uint16_t Length,MaximumLength;} ANSI_STRING;
typedef struct {int unused;} OBJECT_ATTRIBUTES,IO_STATUS_BLOCK;
typedef struct {int width,height,bpp,refresh;} VIDEO_MODE;
struct kernel528 {uint16_t Major,Minor,Build,Qfe;};
extern struct kernel528 XboxKrnlVersion;
#define INVALID_HANDLE_VALUE ((HANDLE)(intptr_t)-1)
#define OBJ_CASE_INSENSITIVE 64
#define NT_SUCCESS(s) ((s)>=0)
#define GENERIC_READ 1
#define GENERIC_WRITE 2
#define FILE_SHARE_READ 4
#define CREATE_NEW 5
#define OPEN_EXISTING 6
#define FILE_ATTRIBUTE_NORMAL 128
#define HalRebootRoutine 1
#define InitializeObjectAttributes(a,b,c,d,e) ((void)(a),(void)(b),(void)(c),(void)(d),(void)(e))
BOOL XVideoSetMode(int,int,int,int);
VIDEO_MODE XVideoGetMode(void);
unsigned char *XVideoGetFB(void);
size_t MmQueryAllocationSize(void *);
void XVideoFlushFB(void);
void debugClearScreen(void);
void debugPrint(const char *,...);
void Sleep(DWORD);
void HalReturnToFirmware(int);
int nxIsDriveMounted(char);
int nxMountDrive(char,const char *);
DWORD GetLastError(void);
void RtlInitAnsiString(ANSI_STRING *,const char *);
NTSTATUS NtOpenSymbolicLinkObject(HANDLE *,OBJECT_ATTRIBUTES *);
NTSTATUS NtQuerySymbolicLinkObject(HANDLE,ANSI_STRING *,ULONG *);
NTSTATUS NtClose(HANDLE);
HANDLE CreateFileA(const char *,DWORD,DWORD,void *,DWORD,DWORD,HANDLE);
int WriteFile(HANDLE,const void *,DWORD,DWORD *,void *);
int ReadFile(HANDLE,void *,DWORD,DWORD *,void *);
NTSTATUS NtFlushBuffersFile(HANDLE,IO_STATUS_BLOCK *);
int CloseHandle(HANDLE);
