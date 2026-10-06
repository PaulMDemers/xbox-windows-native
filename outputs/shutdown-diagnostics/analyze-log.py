"""Parse diagnostic samples and compare the two free-space APIs without guessing disk contents."""
import argparse,json,re
from pathlib import Path
k=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('kind',choices=['emulator','physical']);a=p.parse_args()
path=k/'001/artifacts/probe.log' if a.kind=='emulator' else k/'artifacts/physical/after-probe.log'
text=path.read_bytes().decode('cp1252',errors='backslashreplace');samples=[];sample=None
for line in text.splitlines():
    if line.startswith('SAMPLE '):
        n,t,_=line.split()[1:];sample=dict(index=int(n),elapsed_ms=int(t,16),drives={},commands=[],windows=[]);samples.append(sample)
    if sample is None:continue
    b=re.fullmatch(r'BYTES ([A-Z]):\\ AVAILABLE ([0-9a-f]+) TOTAL ([0-9a-f]+) FREE ([0-9a-f]+)',line)
    if b:sample['drives'].setdefault(b[1],{}).update(available_bytes=int(b[2],16),total_bytes=int(b[3],16),free_bytes=int(b[4],16))
    c=re.fullmatch(r'CLUSTERS ([A-Z]):\\ SPC (\d+) BPS (\d+) FREE (\d+) TOTAL (\d+)',line)
    if c:sample['drives'].setdefault(c[1],{}).update(cluster_bytes=int(c[2])*int(c[3]),free_clusters=int(c[4]),total_clusters=int(c[5]))
    if line.startswith('TARGET '):
        _,drive,target=line.split(' ',2);sample['drives'].setdefault(drive[0],{})['device_target']=target
    if 'newdev.dll,DevInstall' in line:sample['commands'].append(line)
    if line.startswith('WINDOW '):sample['windows'].append(line)
for sample in samples:
    for drive,v in sample['drives'].items():
        v['space_apis_agree']=all(n in v for n in ['free_bytes','total_bytes','free_clusters','total_clusters','cluster_bytes']) and v['free_bytes']==v['free_clusters']*v['cluster_bytes'] and v['total_bytes']==v['total_clusters']*v['cluster_bytes']
        v['free_percent']=100*v['free_bytes']/v['total_bytes'] if v.get('total_bytes') else None
inventory=json.loads((k/'physical-inventory.json').read_text())['mounted_devices']
offsets={0x55f400*512:'E',0x465400*512:'C',0x400*512:'X',0x177400*512:'Y',0x2ee400*512:'Z',15633072*512:'F'}
mapping={name[-2]:offsets.get(v.get('partition_byte_offset')) for name,v in inventory.items() if name.startswith('\\DosDevices\\') and 'partition_byte_offset' in v}
timing_ok=len(samples)==5 and [v['index'] for v in samples]==list(range(5)) and all(v['elapsed_ms']>=v['index']*30000 for v in samples)
r=dict(scope=__doc__,evidence_class=a.kind,samples=samples,captured_physical_drive_mapping=mapping,
       diagnostic_completed=timing_ok and 'COMPLETE 5 ' in text and text.rstrip().endswith('NORMAL_RESTART_REQUEST'),
       limits='Two APIs agreeing is not an independent raw FAT count. Emulator contents differ from physical. Post-run captured registry drive mapping may differ from an earlier fixture; explicit device targets retained. No capacity or installer-state modification.')
(k/(a.kind+'-observations.json')).write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(dict(kind=a.kind,completed=r['diagnostic_completed'],mapping=mapping,last_sample=samples[-1] if samples else None),indent=2))
