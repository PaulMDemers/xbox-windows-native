"""Prepare a separate, still resource-only device-power diagnostic revision."""
from pathlib import Path
k=Path(__file__).resolve().parent;out=k.parent/'lifecycle002';out.mkdir(exist_ok=False)
for name in ('.gitattributes','resources.h','xwnrsc.inf','install.c','probe.c','restart.h','review-build.py','Build-001.ps1'):
    s=(k/name).read_text(encoding='utf-8').replace('lifecycle001','lifecycle002').replace('xwnpcilife1','xwnpcilife2')
    if name=='xwnrsc.inf':s=s.replace('0.1.0.221','0.1.0.222')
    (out/name).write_text(s,encoding='utf-8',newline='\n')
s=(k/'xwnrsc.c').read_text(encoding='utf-8')
s=s.replace('    LONG power_previous;\n    DEVICE_POWER_STATE power_target;', '    LONG diagnostic_power;')
s=s.replace('static NTSTATUS forward(extension *e,PIRP irp,BOOLEAN power)', '''static NTSTATUS NTAPI power_release(PDEVICE_OBJECT device,PIRP irp,PVOID context)
{
    PoStartNextPowerIrp(irp);
    return release(device,irp,context);
}
static NTSTATUS forward(extension *e,PIRP irp,BOOLEAN power)''')
s=s.replace('IoSetCompletionRoutine(irp,release,e,TRUE,TRUE,TRUE);\n    if(power) { PoStartNextPowerIrp(irp); return PoCallDriver(e->lower,irp); }', 'IoSetCompletionRoutine(irp,power ? power_release : release,e,TRUE,TRUE,TRUE);\n    if(power) return PoCallDriver(e->lower,irp);')
start=s.index('static NTSTATUS NTAPI power_complete(')
end=s.index('typedef struct power_work',start)
s=s[:start]+'''typedef struct power_transition {
    extension *e;
    LONG previous;
    DEVICE_POWER_STATE target;
} power_transition;
static NTSTATUS NTAPI power_complete(PDEVICE_OBJECT device,PIRP irp,PVOID context)
{
    power_transition *t=context;extension *e=t->e;
    if(NT_SUCCESS(irp->IoStatus.Status)) {
        POWER_STATE state;state.DeviceState=t->target;
        PoSetPowerState(e->self,DevicePowerState,state);
        InterlockedExchange(&e->powered,t->target==PowerDeviceD0);
    } else InterlockedExchange(&e->powered,t->previous);
    ExFreePool(t);
    /* State update and context use precede readiness for the next NT5 IRP. */
    PoStartNextPowerIrp(irp);
    return release(device,irp,e);
}
static NTSTATUS power_passive(PDEVICE_OBJECT device,PIRP irp)
{
    extension *e=device->DeviceExtension;PIO_STACK_LOCATION sp=IoGetCurrentIrpStackLocation(irp);
    if(sp->MinorFunction==IRP_MN_SET_POWER && sp->Parameters.Power.Type==DevicePowerState) {
        power_transition *t=ExAllocatePoolWithTag(NonPagedPool,sizeof(*t),TAG);
        if(!t){PoStartNextPowerIrp(irp);IoReleaseRemoveLock(&e->remove,irp);return finish(irp,STATUS_INSUFFICIENT_RESOURCES,0);}
        t->e=e;t->target=sp->Parameters.Power.State.DeviceState;
        ExAcquireFastMutex(&e->mutex);
        ++e->powers;t->previous=InterlockedExchange(&e->powered,0);
        ExReleaseFastMutex(&e->mutex);
        IoCopyCurrentIrpStackLocationToNext(irp);
        IoSetCompletionRoutine(irp,power_complete,t,TRUE,TRUE,TRUE);
        return PoCallDriver(e->lower,irp);
    }
    return forward(e,irp,TRUE);
}
''' + s[end:]
# Resource-only test endpoint. It issues genuine power-manager IRPs, not synthetic
# calls into the dispatch routine. Output records the actual completion status.
pos=s.index('static NTSTATUS NTAPI dispatch(')
extra='''typedef struct diagnostic_power {
    extension *e;PIRP irp;ULONG target;
} diagnostic_power;
static VOID NTAPI diagnostic_complete(PDEVICE_OBJECT device,UCHAR minor,POWER_STATE state,PVOID context,PIO_STATUS_BLOCK iosb)
{
    diagnostic_power *d=context;extension *e=d->e;PIRP irp=d->irp;
    ULONG *v=irp->AssociatedIrp.SystemBuffer;
    UNREFERENCED_PARAMETER(device);UNREFERENCED_PARAMETER(minor);UNREFERENCED_PARAMETER(state);
    v[0]=d->target;v[1]=iosb->Status;v[2]=InterlockedCompareExchange(&e->powered,0,0);
    ExFreePool(d);InterlockedExchange(&e->diagnostic_power,0);
    IoReleaseRemoveLock(&e->remove,irp);finish(irp,STATUS_SUCCESS,12);
}
static NTSTATUS diagnostic_request(extension *e,PIRP irp)
{
    PIO_STACK_LOCATION sp=IoGetCurrentIrpStackLocation(irp);ULONG *v=irp->AssociatedIrp.SystemBuffer;
    diagnostic_power *d;POWER_STATE state;NTSTATUS s;
    if(sp->Parameters.DeviceIoControl.InputBufferLength!=8 || sp->Parameters.DeviceIoControl.OutputBufferLength<12 || !v || v[0]!=1 || (v[1]!=PowerDeviceD0 && v[1]!=PowerDeviceD3)) {
        IoReleaseRemoveLock(&e->remove,irp);return finish(irp,STATUS_INVALID_PARAMETER,0);
    }
    d=ExAllocatePoolWithTag(NonPagedPool,sizeof(*d),TAG);
    if(!d){IoReleaseRemoveLock(&e->remove,irp);return finish(irp,STATUS_INSUFFICIENT_RESOURCES,0);}
    ExAcquireFastMutex(&e->mutex);
    if(!e->started || e->shutdown || e->query || InterlockedCompareExchange(&e->diagnostic_power,1,0)) {
        ExReleaseFastMutex(&e->mutex);ExFreePool(d);IoReleaseRemoveLock(&e->remove,irp);return finish(irp,STATUS_DEVICE_NOT_READY,0);
    }
    d->e=e;d->irp=irp;d->target=v[1];state.DeviceState=v[1];
    ExReleaseFastMutex(&e->mutex);IoMarkIrpPending(irp);
    s=PoRequestPowerIrp(e->self,IRP_MN_SET_POWER,state,diagnostic_complete,d,NULL);
    if(s!=STATUS_PENDING){IO_STATUS_BLOCK iosb;iosb.Status=s;iosb.Information=0;diagnostic_complete(e->self,IRP_MN_SET_POWER,state,d,&iosb);}
    return STATUS_PENDING;
}
'''
s=s[:pos]+extra+s[pos:]
needle='    ExAcquireFastMutex(&e->mutex);\n    if(sp->MajorFunction==IRP_MJ_SHUTDOWN)'
s=s.replace(needle,'''    if(sp->MajorFunction==IRP_MJ_DEVICE_CONTROL && sp->Parameters.DeviceIoControl.IoControlCode==CTL_CODE(FILE_DEVICE_UNKNOWN,0x809,METHOD_BUFFERED,FILE_READ_ACCESS)) {
        if(KeGetCurrentIrql()!=PASSIVE_LEVEL){s=STATUS_INVALID_DEVICE_STATE;goto done;}
        return diagnostic_request(e,irp);
    }
''' + needle)
(out/'xwnrsc.c').write_text(s,encoding='utf-8',newline='\n')
