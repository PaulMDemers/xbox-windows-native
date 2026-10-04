"""Read-only cold verification of an owned, stopped cache-regression overlay."""
import argparse,pathlib,sys,subprocess,json,hashlib,importlib.util
ws=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility');k=ws/'outputs/native-windows-physical-f'
p=argparse.ArgumentParser();p.add_argument('--run',required=True);a=p.parse_args()
assert a.run.startswith(('nt5-physical-f-cache-','nt5-physical-f-hives-')) and a.run.replace('-','').isalnum()
run=ws/'work/runs'/a.run;assert (run/'cleanup.json').exists()
raw=pathlib.Path('/home/paul/xbox-windows-native/fixtures')/(a.run+'-audit.raw');assert not raw.exists()
sys.path[:0]=[str(ws/'outputs/native-windows-fatx-runtime'),'/mnt/c/Users/Paul/Desktop/ogxbox-linux/scripts']
import fatx_stage_boot as fatx
from bulk_fatx import Writer
r={'scope':__doc__,'run':a.run,'files':[],'whole_filesystem_audit':False}
try:
    subprocess.run(['qemu-img','convert','-O','raw',str(run/'hdd.qcow2'),str(raw)],check=True)
    with raw.open('rb') as f:
        fatx.PARTITIONS['F']=(15633072*512,472764096*512);w=Writer(f,fatx.open_partition(f,raw,'F'))
        report=w.read('xwn-report-v2.txt');r['report']=report.decode('ascii').rstrip();r['probe_passed']='XWN-CACHE-PASS' in r['report']
        for name in ['xwn-report-v2.txt','winnt/system32/config/sysevent.evt','xwn-cache-append.tmp','xwn-cache-map.tmp','xwn-cache-pressure.tmp']:
            try:data=w.read(name)
            except (KeyError,FileNotFoundError):r['files'].append({'path':name,'present':False});continue
            row={'path':name,'present':True,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
            if name.endswith('append.tmp'):
                row['pattern_match']=data==bytes((i*37+(i>>8)+0x65)&255 for i in range(131073))
            if name.endswith('pressure.tmp'):
                block=bytes((i*37+(i>>8)+0x77)&255 for i in range(65536))
                row['pattern_match']=len(data)==32*1024*1024 and all(data[i:i+65536]==block for i in range(0,len(data),65536))
            if name.endswith('map.tmp'):row['truncated_to_zero']=len(data)==0
            if name.endswith('.evt') or name.endswith('.txt'):
                target=k/'artifacts'/(a.run+'-'+pathlib.Path(name).name)
                if target.exists():assert target.read_bytes()==data
                else:target.write_bytes(data)
            r['files'].append(row)
finally:raw.unlink(missing_ok=True)
(k/(a.run+'-audit.json')).write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
