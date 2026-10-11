"""Freeze a resource-only PnP integration derivative; no controller I/O."""
from pathlib import Path
k=Path(__file__).resolve().parent
old=k.parent/'ownership001'
def write(name,data):
    p=k/name
    assert not p.exists(),p
    p.write_text(data,encoding='utf-8',newline='\n')
write('.gitattributes','* -text whitespace=cr-at-eol\n')
write('resources.h',(old/'resources.h').read_text(encoding='utf-8'))
s=(old/'xwnsmb-resource.c').read_text(encoding='utf-8')
s=s.replace('    LONG started, powered, shutdown, quarantined;', '    ULONG starts, stops, queries, powers;\n    LONG started, powered, shutdown, quarantined;')
s=s.replace('    } else if(sp->Parameters.DeviceIoControl.IoControlCode!=IOCTL_TELEMETRY)', '''    } else if(sp->Parameters.DeviceIoControl.IoControlCode==CTL_CODE(FILE_DEVICE_UNKNOWN,0x808,METHOD_BUFFERED,FILE_READ_ACCESS)) {
        ULONG *v=irp->AssociatedIrp.SystemBuffer;
        if(sp->Parameters.DeviceIoControl.InputBufferLength || sp->Parameters.DeviceIoControl.OutputBufferLength<40) s=STATUS_BUFFER_TOO_SMALL;
        else { v[0]=1;v[1]=e->resource_profile;v[2]=e->port;v[3]=e->started;v[4]=e->powered;
               v[5]=e->starts;v[6]=e->stops;v[7]=e->queries;v[8]=e->powers;v[9]=0;
               s=STATUS_SUCCESS;bytes=40; }
    } else if(sp->Parameters.DeviceIoControl.IoControlCode!=IOCTL_TELEMETRY)''')
s=s.replace('e->started=1; e->powered=1;', '++e->starts; e->started=1; e->powered=1;')
s=s.replace('e->previous=e->query;', '++e->queries; e->previous=e->query;')
s=s.replace('e->started=0; ExReleaseFastMutex(&e->mutex);\n        IoSetDeviceInterfaceState', '++e->stops; e->started=0; ExReleaseFastMutex(&e->mutex);\n        IoSetDeviceInterfaceState')
s=s.replace('e->power_previous=InterlockedExchange', '++e->powers; e->power_previous=InterlockedExchange')
write('xwnrsc.c',s)
s=(k.parent/'xwnsmb.inf').read_text(encoding='utf-8').replace('xwnsmb','xwnrsc').replace('Telemetry','Resources').replace('telemetry','resource-only diagnostics').replace('0.1.0.207','0.1.0.221')
write('xwnrsc.inf',s)
s=(k.parent/'xwnsmb-install.c').read_text(encoding='utf-8').replace('xwnpci207','xwnpcilife1').replace('xwnsmb.inf','xwnrsc.inf')
write('install.c',s)
s=(k.parent/'xwncycle.c').read_text(encoding='utf-8')
write('restart.h',s[s.index('static void guarded_restart(void)\n{'):])
