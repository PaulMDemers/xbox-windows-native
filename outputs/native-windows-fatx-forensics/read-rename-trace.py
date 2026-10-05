"""Capture bounded emulator rename-lookup records, resuming the owned guest afterward."""
import argparse,json,pathlib,struct,sys
k=pathlib.Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(k.parent/'native-windows-prebuild'))
from monitor_capture import command,acquire_monitor_lock
p=argparse.ArgumentParser();p.add_argument('--run',required=True);p.add_argument('--label',default='first');p.add_argument('--filtered',action='store_true');a=p.parse_args()
assert a.run.startswith('nt5-physical-f-high-allocation-') and a.run.replace('-','').isalnum()
assert a.label.replace('-','').isalnum()
run=ws/'work/runs'/a.run;raw=run/'rename-lookup.ram';out=run/('rename-lookup-'+a.label+'.json');assert not raw.exists() and not out.exists()
fields=['status','replace','target_fcb','flags','dir_index','start_index','parent_fcb','first_cluster']
results=[]
with acquire_monitor_lock(4594):
    running='VM status: running' in command(4594,'info status');command(4594,'stop')
    try:
        command(4594,'pmemsave 0 62914560 '+json.dumps(raw.resolve().as_posix()));data=raw.read_bytes();at=0
        while True:
            at=data.find(b'XWN-RENAME-0085\0' if a.filtered else b'XWN-RENAME-0084\0',at)
            if at<0:break
            count=struct.unpack_from('<I',data,at+16)[0];rows=[]
            if 0<count<1000000:
                for i in range(max(0,count-16),count):
                    start=at+20+(i%16)*544
                    row=dict(zip(fields,struct.unpack_from('<8I',data,start)))
                    row['requested']=data[start+32:start+288].decode('utf-16-le',errors='replace').split('\0')[0]
                    row['target']=data[start+288:start+544].decode('utf-16-le',errors='replace').split('\0')[0]
                    rows.append(row)
                results.append(dict(physical_offset=at,count=count,entries=rows))
            at+=16
        out.write_text(json.dumps(dict(scope=__doc__,run=a.run,records=results),indent=2)+'\n');print(json.dumps(results,indent=2))
    finally:
        raw.unlink(missing_ok=True)
        if running:command(4594,'cont')
