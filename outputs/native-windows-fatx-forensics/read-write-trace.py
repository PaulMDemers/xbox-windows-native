"""Capture bounded emulator write-failure records, resuming the owned guest afterward."""
import argparse,json,pathlib,struct,sys
k=pathlib.Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(k.parent/'native-windows-prebuild'))
from monitor_capture import command,acquire_monitor_lock
p=argparse.ArgumentParser();p.add_argument('--run',required=True);a=p.parse_args()
assert a.run.startswith('nt5-physical-f-high-allocation-') and a.run.replace('-','').isalnum()
run=ws/'work/runs'/a.run;raw=run/'write-failure.ram';out=run/'write-failure-trace.json';assert not raw.exists() and not out.exists()
fields=['status','irql','irp_flags','fcb_flags','offset_low','offset_high','length','file_size','allocation_size','first_cluster','file_object','open_handles','dir_index','start_index','is_directory','valid_data_length']
results=[]
with acquire_monitor_lock(4594):
    running='VM status: running' in command(4594,'info status');command(4594,'stop')
    try:
        command(4594,'pmemsave 0 62914560 '+json.dumps(raw.resolve().as_posix()));data=raw.read_bytes();at=0
        while True:
            at=data.find(b'XWN-WRFAIL-0082\0',at)
            if at<0:break
            count=struct.unpack_from('<I',data,at+16)[0];rows=[]
            if 0<count<1000000:
                for i in range(max(0,count-16),count):
                    start=at+20+(i%16)*192
                    row=dict(zip(fields,struct.unpack_from('<16I',data,start)))
                    row['name']=data[start+64:start+192].decode('utf-16-le',errors='replace').split('\0')[0]
                    rows.append(row)
                results.append(dict(physical_offset=at,count=count,entries=rows))
            at+=16
        out.write_text(json.dumps(dict(scope=__doc__,run=a.run,records=results),indent=2)+'\n');print(json.dumps(results,indent=2))
    finally:
        raw.unlink(missing_ok=True)
        if running:command(4594,'cont')
