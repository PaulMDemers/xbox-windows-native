/* SPDX-License-Identifier: MIT -- diagnostic controls only; no controller I/O. */
static NTSTATUS rebalance_probe(extension *e,PIRP irp)
{
    PIO_STACK_LOCATION sp=IoGetCurrentIrpStackLocation(irp);ULONG *v=irp->AssociatedIrp.SystemBuffer,action;
    NTSTATUS s=STATUS_SUCCESS;BOOLEAN notify=FALSE;
    if(KeGetCurrentIrql()!=PASSIVE_LEVEL || !v || sp->Parameters.DeviceIoControl.InputBufferLength!=8 || sp->Parameters.DeviceIoControl.OutputBufferLength<48 || v[0]!=1 || v[1]>3){IoReleaseRemoveLock(&e->remove,irp);return finish(irp,STATUS_INVALID_PARAMETER,0);}
    action=v[1];ExAcquireFastMutex(&e->mutex);
    if(action==3){InterlockedExchange(&e->rebalance,0);InterlockedExchange(&e->stop_veto,0);notify=TRUE;}
    else if(action){
        if(!e->started || !e->powered || e->query || e->shutdown || e->rebalance || e->stop_veto)s=STATUS_DEVICE_NOT_READY;
        else {InterlockedExchange(&e->stop_veto,action==1);InterlockedExchange(&e->rebalance,1);notify=TRUE;}
    }
    v[0]=1;v[1]=e->rebalance;v[2]=e->state_queries;v[3]=e->stop_queries;v[4]=e->stop_cancels;v[5]=e->stop_irps;
    v[6]=e->starts;v[7]=e->started;v[8]=e->powered;v[9]=e->query;v[10]=e->stop_veto;v[11]=e->queries;
    ExReleaseFastMutex(&e->mutex);
    if(notify)IoInvalidateDeviceState(e->pdo);
    IoReleaseRemoveLock(&e->remove,irp);return finish(irp,s,NT_SUCCESS(s)?48:0);
}
