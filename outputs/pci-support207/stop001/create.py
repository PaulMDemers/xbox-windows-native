"""Resource-only PnP rebalance diagnostic; original candidates stay frozen."""
from pathlib import Path
k=Path(__file__).resolve().parent;old=k.parent/'cancel001'
names='xwnrsc.c resources.h install.c probe.c restart.h power-test.h remove-test.h cancel-test.h resource-log.h xwnrsc.inf Build-001.ps1 review-build.py prepare-emulator002.py run-emulator002.py audit-emulator002.py review-pnp002.py Continue-001.ps1 e_allocation.py test-start.c resource-tests.h vectors.h start-vector.h'.split()
for name in names:
    p=k/name;assert not p.exists()
    s=(old/name).read_text().replace('cancel001','stop001').replace('xwnpcican1','xwnpcistp1').replace('4794','4804').replace('4796','4806')
    if name=='xwnrsc.inf':s=s.replace('0.1.0.226','0.1.0.227')
    if name=='xwnrsc.c':
        s=s.replace('PDEVICE_OBJECT lower,self;','PDEVICE_OBJECT lower,self,pdo;\n    LONG rebalance,stop_veto,state_queries,stop_queries,stop_cancels,stop_irps;')
        s=s.replace('e->self=device;','e->self=device;e->pdo=pdo;')
        s=s.replace('static NTSTATUS NTAPI dispatch(PDEVICE_OBJECT device,PIRP irp)','#include "rebalance-kernel.h"\nstatic NTSTATUS NTAPI dispatch(PDEVICE_OBJECT device,PIRP irp)')
        needle='    if(sp->MajorFunction==IRP_MJ_DEVICE_CONTROL && sp->Parameters.DeviceIoControl.IoControlCode==CTL_CODE(FILE_DEVICE_UNKNOWN,0x80a,METHOD_BUFFERED,FILE_READ_ACCESS))return hal_probe(e,irp);'
        assert needle in s;s=s.replace(needle,needle+'\n    if(sp->MajorFunction==IRP_MJ_DEVICE_CONTROL && sp->Parameters.DeviceIoControl.IoControlCode==CTL_CODE(FILE_DEVICE_UNKNOWN,0x80b,METHOD_BUFFERED,FILE_READ_ACCESS))return rebalance_probe(e,irp);')
        needle='    case IRP_MN_FILTER_RESOURCE_REQUIREMENTS:'
        s=s.replace(needle,'''    case IRP_MN_QUERY_PNP_DEVICE_STATE:
        irp->IoStatus.Status=STATUS_SUCCESS;s=forward_wait(e,irp);
        InterlockedIncrement(&e->state_queries);
        if(NT_SUCCESS(s) && InterlockedExchange(&e->rebalance,0)) {
            /* Documented combination requests STOP before resource reassignment. */
            irp->IoStatus.Information|=PNP_DEVICE_FAILED|PNP_DEVICE_RESOURCE_REQUIREMENTS_CHANGED;
            trace_resources(6,0,(NTSTATUS)irp->IoStatus.Information,NULL,0,NULL,0);
        }
        irp->IoStatus.Status=s;IoReleaseRemoveLock(&e->remove,irp);IoCompleteRequest(irp,IO_NO_INCREMENT);return s;
'''+needle)
        s=s.replace('    case IRP_MN_QUERY_STOP_DEVICE:\n', '''    case IRP_MN_QUERY_STOP_DEVICE:
        InterlockedIncrement(&e->stop_queries);
        if(InterlockedExchange(&e->stop_veto,0)) {
            trace_resources(7,IRP_MN_QUERY_STOP_DEVICE,STATUS_UNSUCCESSFUL,NULL,0,NULL,0);
            IoReleaseRemoveLock(&e->remove,irp);return finish(irp,STATUS_UNSUCCESSFUL,0);
        }
''')
        s=s.replace('    case IRP_MN_CANCEL_STOP_DEVICE:\n','    case IRP_MN_CANCEL_STOP_DEVICE:\n        InterlockedIncrement(&e->stop_cancels);\n')
        s=s.replace('if(NT_SUCCESS(s)) { ExAcquireFastMutex(&e->mutex); e->query=e->previous; ExReleaseFastMutex(&e->mutex); }','if(NT_SUCCESS(s)) { ExAcquireFastMutex(&e->mutex); if(e->query==(sp->MinorFunction==IRP_MN_CANCEL_STOP_DEVICE?IRP_MN_QUERY_STOP_DEVICE:IRP_MN_QUERY_REMOVE_DEVICE))e->query=e->previous; ExReleaseFastMutex(&e->mutex); }')
        s=s.replace('    case IRP_MN_STOP_DEVICE:\n','    case IRP_MN_STOP_DEVICE:\n        InterlockedIncrement(&e->stop_irps);\n')
    if name=='probe.c':
        s=s.replace('#include "cancel-test.h"','#include "rebalance-test.h"\n#include "cancel-test.h"')
        s=s.replace('    /* Read capabilities of the exact instance retained above. */','    if(!exercise_rebalance(dev.DevInst))ExitProcess(40);\n    /* Read capabilities of the exact instance retained above. */')
    if name=='review-pnp002.py':
        s=s.replace("r['pnp_restart_api_succeeded']=","r['stop_cancel_qualified']=all(x in log.splitlines() for x in ('REBALANCE_STOP_RECOVERED','REBALANCE_CANCEL_RECOVERED')) and all(any(x['stage']==5 and x['profile']==minor for x in records) for minor in (4,5,6))\nr['pnp_restart_api_succeeded']=")
    if name=='Continue-001.ps1':s=s.replace('!$r.cancel_remove_qualified','!$r.cancel_remove_qualified -or !$r.stop_cancel_qualified')
    p.write_text(s,newline='\n')
(k/'.gitattributes').write_text('* -text whitespace=cr-at-eol\n')
