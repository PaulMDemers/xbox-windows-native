"""Join immutable physical records to actual image bytes, then inspect independently."""
import hashlib,json,shutil,struct,subprocess
from pathlib import Path
from inspect import inspect
K=Path(__file__).resolve().parent;W=K.parents[1];OUT=K/'review001.json'
assert not OUT.exists();assert shutil.disk_usage('C:/').free-8*1024**2>=20*1024**3
pins={};sha=lambda b:hashlib.sha256(b).hexdigest()
def read(p):
 p=Path(p);b=p.read_bytes();pins[str(p.resolve())]=sha(b);return b
def js(p):return json.loads(read(p))
images={};orig={};joins={}
specs=[('483','handoff-witness483','physical001-stage.json','physical001-collection.json','C:/xwn483/build001/default.xbe','/E/Applications/XWNBoot483a/default.xbe'),
 ('487','blend-precision487','stage001.json','collection-completed002.json','C:/xwn487/build001/default.xbe','/E/Applications/XWNBoot487a/default.xbe'),
 ('494','d3d-transform494','physical001-stage.json','physical001-collection.json','C:/xwn494/build002/default.xbe','/E/Applications/XWNBoot494a/default.xbe'),
 ('501','entry-scene501','physical001-stage.json','physical001-collection.json','C:/xwn499/build001/default.xbe','/E/Applications/XWNBoot499a/default.xbe'),
 ('508','entry-physical508','physical001-stage.json','physical001-collection.json','C:/xwn504/build001/default.xbe','/E/Applications/XWNBoot504a/default.xbe')]
for label,folder,sn,cn,built,remote in specs:
 s=js(K.parent/folder/sn);c=js(K.parent/folder/cn);row=c['files'][remote]
 b=read(built);cold=read(row['path']);assert b==cold and sha(b)==row['sha256']==s['staged'][remote]['sha256']
 orig[label]=b;images[label]=inspect(b);joins[label]=dict(build=built,cold=row['path'],stage=str(K.parent/folder/sn),collection=str(K.parent/folder/cn),equal=True)
s=js(K.parent/'entry-physical508/physical001-stage.json');row=s['before']['/E/Applications/XWNEBoot/default.xbe'];b=read(row['path']);assert sha(b)==row['sha256'];orig['ordinary']=b;images['ordinary']=inspect(b)
for n in ['handoff-witness483/REPORT.md','handoff-witness483/actual-witness001.json','d3d-transform494/REPORT.md','d3d-transform494/actual-context001.json','entry-physical508/final-review.json','entry-return507/emu001/trace.json','entry-return507/actual-review001.json']:read(K.parent/n)
for p in ['C:/nxdk/tools/cxbe/Xbe.h','C:/nxdk/tools/cxbe/Xbe.cpp','C:/nxdk/lib/xboxkrnl/xboxkrnl.h','C:/nxdk/lib/xboxkrnl/xboxkrnl.exe.def']:read(p)
sdkcommit=subprocess.check_output(['git','-C','C:/nxdk','rev-parse','HEAD'],text=True).strip();assert sdkcommit.startswith('58427c')
kernel=js(K.parent/'hd-timing-capture307/kernel-review001.json')
exports={str(n):kernel['exports'][str(n)] for n in sorted(set(sum((v['imports'] for v in images.values()),[])))}
diffs={}
for label,r in images.items():
 diffs[label]=[f'0x{o:03x}' for o in range(0x104,0x178,4) if r['header_fields'][f'{o:03x}']!=images['494']['header_fields'][f'{o:03x}']]
assert set(diffs['508'])=={'0x10c','0x128'} and set(diffs['501'])=={'0x10c','0x128'}
assert len({r['certificate_sha256'] for r in images.values()})==1
assert len({r['tls_bytes_sha256'] for r in images.values()})==1 and all(not r['tls_generic_in_image_range_check'] for r in images.values())
assert all(images[n]['entry']==0x11100 for n in ['483','487','494','ordinary'])
assert images['501']['entry']==0x94877 and images['508']['entry']==0x94aff
symbols={}
for label,path in [('494','C:/xwn494/build002/symbols.txt'),('504','C:/xwn504/build001/symbols.txt')]:
 symbols[label]={a[2]:int(a[0],16) for line in read(path).decode().splitlines() if len(a:=line.split())==3}
assert symbols['494']['capture490_begin']==0x9473e and symbols['494']['capture490_end']==0x94877
assert symbols['494']['capture490_begin']&~4095==images['508']['entry_page']==0x94000
assert images['494']['rounded_image_end']==0x95000 and images['508']['rounded_image_end']==0x96000
assert symbols['504']['entry498_record']==0x95000
neg=[]
for label,b in orig.items():
 so=struct.unpack_from('<I',b,0x120)[0]-0x10000
 mutations=[('magic',0,0),('base',0x104,0),('headers',0x108,0),('image',0x10c,len(b)+1),('image-header',0x110,0),('sections',0x11c,2),('section-pointer',0x120,0xffffffff),('entry',0x128,0xffffffff^0xa8fc57ab),('tls-pointer',0x12c,0xffffffff),('thunk-pointer',0x158,0xffffffff^0x5b6d40b6),('flags',so,3),('section-va',so+4,0x12000),('virtual-size',so+8,0xffffffff),('raw-offset',so+12,0),('raw-size',so+16,0xffffffff),('section-name',so+20,0xffffffff),('head-ref',so+28,0xffffffff),('tail-ref',so+32,0xffffffff),('certificate',0x118,0xffffffff)]
 for name,off,value in mutations:
  d=bytearray(b);struct.pack_into('<I',d,off,value)
  try:inspect(bytes(d))
  except ValueError:neg.append(dict(image=label,case=name));continue
  raise AssertionError((label,name))
 for off in list(range(so+36,so+56))+list(range(0x1000,len(b),4096)):
  d=bytearray(b);d[off]^=1
  try:inspect(bytes(d))
  except ValueError:neg.append(dict(image=label,case='digest-byte',offset=off));continue
  raise AssertionError((label,off))
 for size in [0,0x177,0xfff,len(b)-1]:
  try:inspect(b[:size])
  except ValueError:neg.append(dict(image=label,case='truncated',bytes=size));continue
  raise AssertionError((label,size))
for p in K.glob('*.py'):read(p)
assert all(sha(Path(n).read_bytes())==h for n,h in pins.items())
r=dict(passed=True,scope='independent static family structure and prior physical-file joins; no loader/ABI cause established',physical_access=False,build=False,new_launch=False,images=images,physical_joins=joins,header_DWORD_differences_from494=diffs,negative_controls=len(neg),mutations=neg,source_pins=pins,sdk_commit=sdkcommit,
 physical_kernel_historical=dict(version=kernel['actual_kernel_version'],image_size=kernel['image_size'],timestamp=kernel['timestamp'],missing_pages=kernel['missing_pages'],exports=exports,raw_kernel_rehashed=False,current_kernel_identity_remeasured=False),
 common_TLS_anomaly='same payload bytes interpreted as TLS fail generic in-image range checks in every image, including successes; runtime TLS handling unknown',
 entry_address_is_only_hypothesis=True,low_entry_487_also_failed=True,successful494_executed_same_94000_code_page=True,new_entry_data_page_95000=True,
 same_high_page_execution_not_proof_of_new_data_page_or_initial_entry=True,root_cause_established=False,all_originals_unchanged=True)
OUT.write_bytes((json.dumps(r,indent=2)+'\n').encode());print('PASS',len(images),'actual images;',len(neg),'negative structural/digest mutations')
