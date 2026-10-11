/* SPDX-License-Identifier: MIT
 * Disposable PnP diagnostic: preserve OS-supplied bytes before rejection.
 * PASSIVE_LEVEL only, capped at 64 records. No controller access.
 */
static LONG trace_records;
static ULONG resource_bytes(PCM_RESOURCE_LIST p)
{
    if(!p)return 0;
    if(p->Count!=1)return 4;
    if(p->List[0].PartialResourceList.Count>16)return 20;
    return 20+16*p->List[0].PartialResourceList.Count;
}
static void trace_resources(ULONG stage,ULONG profile,NTSTATUS status,
                            PVOID first,ULONG first_size,PVOID second,ULONG second_size)
{
    UNICODE_STRING path;OBJECT_ATTRIBUTES attributes;IO_STATUS_BLOCK iosb;
    HANDLE file;ULONG header[7];NTSTATUS s;
    if(KeGetCurrentIrql()!=PASSIVE_LEVEL || InterlockedIncrement(&trace_records)>64)return;
    if(first_size>1024)first_size=1024;
    if(second_size>1024)second_size=1024;
    header[0]=0x52574e58;header[1]=stage;header[2]=profile;header[3]=status;
    header[4]=first_size;header[5]=second_size;header[6]=trace_records;
    RtlInitUnicodeString(&path,L"\\??\\C:\\xwnpcilife4\\resource-trace.bin");
    InitializeObjectAttributes(&attributes,&path,OBJ_CASE_INSENSITIVE|OBJ_KERNEL_HANDLE,NULL,NULL);
    s=ZwCreateFile(&file,FILE_APPEND_DATA|SYNCHRONIZE,&attributes,&iosb,NULL,
                   FILE_ATTRIBUTE_NORMAL,FILE_SHARE_READ,FILE_OPEN_IF,
                   FILE_SYNCHRONOUS_IO_NONALERT|FILE_NON_DIRECTORY_FILE|FILE_WRITE_THROUGH,NULL,0);
    if(!NT_SUCCESS(s))return;
    s=ZwWriteFile(file,NULL,NULL,NULL,&iosb,header,sizeof(header),NULL,NULL);
    if(NT_SUCCESS(s) && first_size)s=ZwWriteFile(file,NULL,NULL,NULL,&iosb,first,first_size,NULL,NULL);
    if(NT_SUCCESS(s) && second_size)(void)ZwWriteFile(file,NULL,NULL,NULL,&iosb,second,second_size,NULL,NULL);
    ZwClose(file);
}
