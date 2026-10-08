"""Test actual page oracle on preserved failure RAM; reject code and mapping mutations."""
import hashlib,json,sys
from pathlib import Path
from residency import inspect_display,physical,table
k=Path(__file__).resolve().parent;ws=k.parents[1];old=k.parent/'video-ram-crash2/crash001'
sys.path.insert(0,str(ws/'work/python-packages'));import pefile
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=read(old/'failure-residency.json');p=Path(m['private_memory']);assert sha(p)==m['private_memory_sha256'];ram=p.read_bytes();r=read(old/'residency-analysis.json')
info=read(k/'modules.json')['xwnown.dll'];pe=pefile.PE(info['path']);assert sha(Path(info['path']))==info['sha256'];cr3=r['current_cr3'];base=r['display_base']
baseline=inspect_display(ram,cr3,base,pe,info['symbols']);assert baseline['mapped_bytes']==7572 and baseline['unmapped_bytes']==4096
rejected=[]
for name in ['code_byte','required_page','invented_first_page']:
 data=bytearray(ram);va=base+info['symbols']['XwnUpload'];pde=table(ram,cr3&~4095)[va>>22];pt=pde&~4095
 if name=='code_byte':data[physical(ram,cr3,va)]^=1
 elif name=='required_page':data[pt+4*((va>>12)&1023)]&=254
 else:data[pt+4*(((base+4096)>>12)&1023)]|=1
 try:inspect_display(bytes(data),cr3,base,pe,info['symbols'])
 except AssertionError:rejected.append(name)
 else:raise AssertionError('Mutation accepted: '+name)
out=dict(passed=True,mapped_bytes=7572,unmapped_bytes=4096,rejected=rejected,
 oracle_sha256=sha(k/'residency.py'),source_snapshot_sha256=sha(p),module_sha256=info['sha256'],limits='Existing failed-case snapshot only; new run remains unqualified.')
dest=k/'residency-tests.json';assert not dest.exists();dest.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
