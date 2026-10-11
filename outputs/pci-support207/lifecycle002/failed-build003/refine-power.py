"""Reserve SET_POWER storage/work item at AddDevice, before any power IRP."""
from pathlib import Path
k=Path(__file__).resolve().parent;p=k/'xwnrsc.c';s=p.read_text(encoding='utf-8')
s=s.replace('typedef struct extension {','''typedef struct extension extension;
typedef struct power_transition {
    extension *e;
    LONG previous;
    DEVICE_POWER_STATE target;
} power_transition;
struct extension {''',1)
s=s.replace('    LONG diagnostic_power;\n} extension;', '''    LONG diagnostic_power;
    power_transition transition;
    PIO_WORKITEM power_work;
    PIRP power_irp;
};''')
dup='''typedef struct power_transition {
    extension *e;
    LONG previous;
    DEVICE_POWER_STATE target;
} power_transition;
'''
pos=s.index(dup,s.index(dup)+len(dup));s=s[:pos]+s[pos:].replace(dup,'',1)
s=s.replace('    ExFreePool(t);\n    /* State update', '    /* State update')
s=s.replace('''        power_transition *t=ExAllocatePoolWithTag(NonPagedPool,sizeof(*t),TAG);
        if(!t){PoStartNextPowerIrp(irp);IoReleaseRemoveLock(&e->remove,irp);return finish(irp,STATUS_INSUFFICIENT_RESOURCES,0);}
''','''        /* NT5 readiness stays closed through completion. One reserved context
         * therefore belongs to exactly one outstanding SET_POWER at a time. */
        power_transition *t=&e->transition;
''')
start=s.index('typedef struct power_work')
end=s.index('static NTSTATUS NTAPI add(',start)
s=s[:start]+'''static VOID NTAPI power_worker(PDEVICE_OBJECT device,PVOID context)
{
    extension *e=context;PIRP irp=e->power_irp;
    e->power_irp=NULL;
    (void)power_passive(device,irp);
}
static NTSTATUS NTAPI power(PDEVICE_OBJECT device,PIRP irp)
{
    extension *e=device->DeviceExtension;PIO_STACK_LOCATION sp=IoGetCurrentIrpStackLocation(irp);
    NTSTATUS s=IoAcquireRemoveLock(&e->remove,irp);
    if(!NT_SUCCESS(s)){PoStartNextPowerIrp(irp);return finish(irp,s,0);}
    if(sp->MinorFunction!=IRP_MN_SET_POWER || sp->Parameters.Power.Type!=DevicePowerState)
        return forward(e,irp,TRUE);
    if(KeGetCurrentIrql()!=PASSIVE_LEVEL){
        e->power_irp=irp;IoMarkIrpPending(irp);
        IoQueueWorkItem(e->power_work,power_worker,DelayedWorkQueue,e);
        return STATUS_PENDING;
    }
    return power_passive(device,irp);
}
''' +s[end:]
s=s.replace('            IoUnregisterShutdownNotification(device);', '            IoFreeWorkItem(e->power_work);\n            IoUnregisterShutdownNotification(device);')
s=s.replace('    device->Flags |= DO_BUFFERED_IO|DO_POWER_PAGABLE;', '''    e->power_work=IoAllocateWorkItem(device);
    if(!e->power_work){IoUnregisterShutdownNotification(device);RtlFreeUnicodeString(&e->link);IoDetachDevice(e->lower);IoDeleteDevice(device);return STATUS_INSUFFICIENT_RESOURCES;}
    device->Flags |= DO_BUFFERED_IO|DO_POWER_PAGABLE;''')
p.write_text(s,encoding='utf-8',newline='\n')
