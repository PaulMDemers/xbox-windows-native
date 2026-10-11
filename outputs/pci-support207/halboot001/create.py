"""Create fresh controlled HAL boot trials from the closed lifecycle004 harness."""
from pathlib import Path
k=Path(__file__).resolve().parent;old=k.parent/'lifecycle004'
names='xwnrsc.c resources.h install.c probe.c restart.h power-test.h remove-test.h resource-log.h xwnrsc.inf Build-001.ps1 review-build.py prepare-emulator.py run-emulator.py audit-emulator.py review-pnp.py test-start.c resource-tests.h vectors.h start-vector.h'.split()
kernel='''
/* PASSIVE_LEVEL only. Fixed invalid request proves ABI rejection without I/O. */
static NTSTATUS hal_probe(extension *e,PIRP irp)
{
    typedef NTSTATUS (NTAPI *read_v1)(ULONG,ULONG,PULONG);
    PIO_STACK_LOCATION sp=IoGetCurrentIrpStackLocation(irp);
    ULONG *v=irp->AssociatedIrp.SystemBuffer;UNICODE_STRING name;read_v1 call;
    NTSTATUS s=STATUS_SUCCESS;
    if(KeGetCurrentIrql()!=PASSIVE_LEVEL)s=STATUS_INVALID_DEVICE_STATE;
    else if(sp->Parameters.DeviceIoControl.InputBufferLength || sp->Parameters.DeviceIoControl.OutputBufferLength<24 || !v)s=STATUS_INVALID_PARAMETER;
    else {
        RtlZeroMemory(v,24);RtlInitUnicodeString(&name,L"XwnSmbusReadV1");
        call=(read_v1)MmGetSystemRoutineAddress(&name);
        v[0]=call!=NULL;
        if(call)v[1]=call(0xff,0xff,v+2);
    }
    IoReleaseRemoveLock(&e->remove,irp);
    return finish(irp,s,NT_SUCCESS(s)?24:0);
}
'''
probe='''
    { DWORD h[6],got=0;char expected[4];DWORD n;BOOL h_ok;
      const char *labels[]={"hal_export=","hal_invalid_ntstatus=","hal_invalid_result=","hal_invalid_status=","hal_invalid_polls=","hal_invalid_data="};
      clear_bytes(h,sizeof(h));clear_bytes(expected,sizeof(expected));
      n=GetEnvironmentVariableA("XWN_HAL_EXPECT",expected,sizeof(expected));
      h_ok=DeviceIoControl(file,CTL_CODE(FILE_DEVICE_UNKNOWN,0x80a,METHOD_BUFFERED,FILE_READ_ACCESS),NULL,0,h,sizeof(h),&got,NULL);
      number("hal_probe_ok=",h_ok);number("hal_probe_error=",h_ok?0:GetLastError());number("hal_probe_bytes=",got);
      if(h_ok)for(i=0;i<6;++i)number(labels[i],h[i]);
      ok=ok && n==1 && (expected[0]=='0'||expected[0]=='1') && h_ok && got==sizeof(h) && h[0]==(DWORD)(expected[0]-'0') && !h[1] && h[2]==h[0] && !h[3] && !h[4] && !h[5];
    }
'''
variant="\nvariant=sys.argv[1];assert variant in ('control','candidate')\n"
for name in names:
    p=k/name;assert not p.exists()
    s=(old/name).read_text().replace('lifecycle004','halboot001').replace('xwnpcilife4','xwnpcihal1').replace('4774','4784').replace('4776','4786')
    if name=='xwnrsc.inf':s=s.replace('0.1.0.224','0.1.0.225')
    if name=='xwnrsc.c':
        needle='static NTSTATUS NTAPI dispatch(PDEVICE_OBJECT device,PIRP irp)';assert needle in s;s=s.replace(needle,kernel+'\n'+needle)
        needle='    ExAcquireFastMutex(&e->mutex);\n    if(sp->MajorFunction==IRP_MJ_SHUTDOWN)'
        assert needle in s
        s=s.replace(needle,'    if(sp->MajorFunction==IRP_MJ_DEVICE_CONTROL && sp->Parameters.DeviceIoControl.IoControlCode==CTL_CODE(FILE_DEVICE_UNKNOWN,0x80a,METHOD_BUFFERED,FILE_READ_ACCESS))return hal_probe(e,irp);\n'+needle)
    if name=='probe.c':
        needle='    CloseHandle(file);return ok;';assert needle in s;s=s.replace(needle,probe+needle)
    if name=='run-emulator.py':s=s.replace('import datetime,','import sys,datetime,')
    if name in ('prepare-emulator.py','run-emulator.py','audit-emulator.py','review-pnp.py'):
        s=s.replace('k=Path(__file__).resolve().parent','k=Path(__file__).resolve().parent'+variant+'k=k')
        s=s.replace("k/'emulator001'","k/(variant+'001')")
    if name=='prepare-emulator.py':
        needle="m.target=source;io=m.SliceIO(source);w=m.Writer(io,m.fatx.open_partition(io,source,'F'))"
        inject="""hal_record=read(k.parent/'handoff001/build001.json')
hal_path=k.parent/('handoff001/artifacts/build001/native/artifacts/halxboxnt5.dll' if variant=='control' else 'handoff001/artifacts/build001/halxboxnt5.dll')
hal_digest=next(x['sha256'] for x in hal_record['baseline']['artifacts'] if x['name']=='halxboxnt5.dll') if variant=='control' else hal_record['candidate_sha256']
assert sha(hal_path)==hal_digest
m.target=source;io=m.SliceIO(source);ew=m.Writer(io,m.fatx.open_partition(io,source,'E'))
restore(ew,'Applications/XWNFBoot/loader/halxboxnt5.dll',hal_path.read_bytes());ew.flush()
files['E/Applications/XWNFBoot/loader/halxboxnt5.dll']=hal_digest
"""
        assert needle in s;s=s.replace(needle,inject+needle)
        needle="(art/'startup.cmd').write_bytes(data)"
        assert needle in s;s=s.replace(needle,"data=data.replace(b'@echo off\\r\\n',b'@echo off\\r\\nset XWN_HAL_EXPECT='+ (b'0' if variant=='control' else b'1') +b'\\r\\n')\n"+needle)
        s=s.replace('resource_only_driver_installation=True','resource_only_driver_installation=True,hal_variant=variant,hal_sha256=hal_digest,hal_build_record_sha256=sha(k.parent/\'handoff001/build001.json\')')
    if name=='review-pnp.py':
        s=s.replace("r['pnp_restart_api_succeeded']=", "r['hal_probe_expected_export']=int(variant=='candidate')\nr['hal_probe_passed']=all(x in log.splitlines() for x in ('hal_probe_ok=1','hal_probe_bytes=24','hal_export='+str(int(variant=='candidate')),'hal_invalid_ntstatus=0','hal_invalid_result='+str(int(variant=='candidate')),'hal_invalid_status=0','hal_invalid_polls=0','hal_invalid_data=0'))\nr['pnp_restart_api_succeeded']=")
        s=s.replace('No telemetry, HAL candidate boot, ordinary cold-boot or physical qualification.','Invalid-request HAL ABI probe only; no controller transactions, terminal takeover, ordinary cold-boot or physical qualification.')
    p.write_text(s,newline='\n')
(k/'.gitattributes').write_text('* -text whitespace=cr-at-eol\n')
