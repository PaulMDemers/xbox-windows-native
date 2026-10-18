"""One complete cold mapping comparison and FATX allocation audit; no guest boot."""
import json,subprocess,sys,hashlib
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('/mnt/c/xwn512/cold001');assert not P.exists()
P.mkdir();run=Path('/mnt/c/xwn512/runs/nt5-entry512-emu001');out=K/'emu001/audit.json';assert not out.exists() and (run/'cleanup.json').exists()
sys.path.insert(0,str(W/'outputs/video-text-oracle206'));from common import ColdIO,sha
sys.path.insert(0,str(W/'outputs/release-readiness403'));from stock_io002 import scan,readers
from entry_decode import decode
prep=json.loads((K/'preparation001.json').read_text());source=Path(prep['seed']);child=run/'hdd.qcow2';assert sha(source)==prep['seed_sha256']
host=json.loads((run/'host-exit.json').read_text());assert host['passed'] and host['closed']
for p,h in json.loads((K/'emu001/frozen.json').read_text()).items():assert sha(W/p)==h,p
mapping=json.loads(subprocess.check_output(['qemu-img','map','--output=json',str(child)]));size=json.loads(subprocess.check_output(['qemu-img','info','--output=json',str(child)]))['virtual-size']
assert sum(v['length'] for v in mapping)==size
cursor=0;examined=0;changed=0;first=[];outside_reserved=0
with ColdIO(source) as before,ColdIO(child) as after:
    for row in mapping:
        assert row['start']==cursor;cursor+=row['length']
        if row['depth']!=0:continue
        for pos in range(row['start'],row['start']+row['length'],65536):
            n=min(65536,row['start']+row['length']-pos);before.seek(pos);after.seek(pos);a=before.read(n);b=after.read(n);examined+=n
            if a!=b:
                (P/f'{pos:012x}-before.bin').write_bytes(a);(P/f'{pos:012x}-after.bin').write_bytes(b)
                for i,(x,y) in enumerate(zip(a,b)):
                    if x!=y:
                        changed+=1;outside_reserved+=not(1536<=pos+i<2048)
                        if len(first)<128:first.append(dict(offset=pos+i,before=x,after=y))
scan(child,P/'allocation/artifacts');allocation=json.loads((P/'allocation/allocation.json').read_text())
with ColdIO(child) as io:
    w=readers(io,child)['E'];candidate=w.read('Applications/XWNBoot510a/default.xbe')
    assert candidate==Path('/mnt/c/xwn510/build001/default.xbe').read_bytes()
    receipts={}
    for name in ['entry.bin','report.bin','witness.bin','context.bin','refusal.bin']:
        try:data=w.read('Applications/XWNBoot510a/'+name)
        except KeyError:receipts[name]={'present':False};continue
        (P/name).write_bytes(data);receipts[name]={'present':True,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
        if name=='entry.bin':
            try:receipts[name]['decoded']=decode(data)
            except ValueError as exc:receipts[name]['decode_error']=str(exc)
    trace=json.loads((K/'emu001/trace.json').read_text())
    memory=next((v for v in trace['reads'] if v['label']=='entry-memory-receipt'),None)
    if memory and receipts['entry.bin']['present']:
        receipts['entry.bin']['memory_exact']=sha(P/'entry.bin')==memory['sha256']

r=dict(candidate_exact=True,receipts=receipts,closed=True,host_exit=host,complete_virtual_mapping_bytes=size,local_extent_bytes_compared=examined,changed_bytes=changed,first_differences=first,changes_outside_reserved_sector=outside_reserved,filesystem_bytes_inherited_unchanged=outside_reserved==0,strict_whole_disk_equal=changed==0,allocation=allocation,qcow_check=json.loads(subprocess.check_output(['qemu-img','check','--output=json',str(child)])),source_sha256=sha(source),source_unchanged=True,eeprom_unchanged=sha(run/'eeprom.bin')==sha(Path('/mnt/e/xwn289/fixture001/hd.bin')),child_sha256=sha(child),physical_access=False,normal_guest_shutdown=False,stopped_before_original_preparation=True,private_cold_files={str(p):sha(p) for p in P.rglob('*') if p.is_file()})
with out.open('x') as f:json.dump(r,f,indent=2);f.write('\n')
print(json.dumps({k:r[k] for k in ['closed','changed_bytes','first_differences','filesystem_bytes_inherited_unchanged','strict_whole_disk_equal','eeprom_unchanged']}))
