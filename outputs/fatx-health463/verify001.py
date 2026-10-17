"""Verify captured bytes and exercise the unchanged analyzer on corrupted copies."""
import array
import hashlib
import json
import struct
import subprocess
import sys
from pathlib import Path

K=Path(__file__).resolve().parent;W=K.parents[1]
P=W/'work/fatx-health463/controls001'
A=W/'outputs/hd-phase-runtime346/analyze-allocation002.py'
sha=lambda b:hashlib.sha256(b).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
assert not P.exists() and not (K/'verification001.json').exists()
c=read(K/'collection002.json');assert c['completed']
for p,h in read(K/'preflight002.json')['source_pins'].items():assert sha(Path(p).read_bytes())==h
data={}
for n,v in c['files'].items():
    data[n]=Path(v['path']).read_bytes()
    assert len(data[n])==v['bytes'] and sha(data[n])==v['sha256']
r=read(K/'allocation002.json')
assert sha((K/'allocation002.json').read_bytes())==c['allocation_sha256']
assert r['allocation_consistent'] and not r['bad_clusters'] and not r['errors'] and not r['orphan_cluster_count']
meta=data['fat-metadata.bin'];blob=data['directories.bin']
fat=array.array('I');fat.frombytes(meta[4096:]);assert sys.byteorder=='little'
limit=(10000048*512-len(meta))//16384+1
free=[i for i in range(1,limit) if fat[i]==0]
entries=[]
for at in range(0,len(blob),80):
    if struct.unpack_from('<I',blob,at)[0]==2:
        e=blob[at+16:at+80]
        first,size=struct.unpack_from('<II',e,44)
        if not e[1]&16 and first and size:entries.append((at,first,size))
assert len(entries)>2 and free
P.mkdir(parents=True)
results=[]
for name in ['orphan','root-free','crosslink','oversize','bad-name']:
    d=P/name;d.mkdir();m=bytearray(meta);b=bytearray(blob)
    if name=='orphan':struct.pack_into('<I',m,4096+free[0]*4,0xffffffff)
    elif name=='root-free':struct.pack_into('<I',m,4096+4,0)
    elif name=='crosslink':struct.pack_into('<I',b,entries[1][0]+16+44,entries[0][1])
    elif name=='oversize':struct.pack_into('<I',b,entries[0][0]+16+48,0xffffffff)
    elif name=='bad-name':b[entries[0][0]+16]=43
    for n,v in [('fat-metadata.bin',m),('directories.bin',b),('snapshot.txt',data['snapshot.txt'])]:
        (d/n).write_bytes(v)
    proc=subprocess.run([sys.executable,'-B',str(A),'--capture',str(d),'--output',str(d/'result.json')],capture_output=True,text=True)
    (d/'stdout.txt').write_text(proc.stdout,encoding='utf-8')
    (d/'stderr.txt').write_text(proc.stderr,encoding='utf-8')
    result=read(d/'result.json') if (d/'result.json').exists() else None
    rejected=proc.returncode!=0 or not result['allocation_consistent']
    assert rejected,name
    results.append(dict(case=name,rejected=rejected,exit_code=proc.returncode,errors=None if result is None else result['errors'],orphan_count=None if result is None else result['orphan_cluster_count']))
for n,v in c['files'].items():assert Path(v['path']).read_bytes()==data[n]
out=dict(passed=True,physical_E_allocation_consistent=True,original_captures_unchanged=True,
         synthetic_corruption_controls=results,free_clusters=len(free),free_bytes=len(free)*16384,
         marked_bad_clusters=r['bad_clusters'],full_surface_media_scan=False,full_file_content_audit=False,
         console_F_allocation_audited=False,console_C_accessed=False,repairs_performed=False,
         before_after_unchanged_files=len(c['unchanged']),source_sha256=sha(Path(__file__).read_bytes()))
(K/'verification001.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:out[k] for k in ['passed','free_bytes','before_after_unchanged_files']}))
