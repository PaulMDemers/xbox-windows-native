from pathlib import Path
import re,json,hashlib,datetime
k=Path('outputs/native-batch738');old=Path('outputs/native-prework737');kernel=Path('outputs/batch-prefix733')
clean=lambda s:re.sub(r'\s+','',re.sub(r'/\*.*?\*/','',s,flags=re.S))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a=(kernel/'probe.c').read_text().replace('733','738').replace('(o->cr0&0x80000001)!=0x80000001 || (o->cr4&0x20)','(o->cr0&0xe0000001)!=0x40000001 || o->cr3!=0 || (flags&0x200) || (o->cr4&0x20)')
assert clean(a)==clean((k/'probe.c').read_text())
assert clean((kernel/'probe.h').read_text().replace('733','738'))==clean((k/'probe.h').read_text())
for n in ['main.c','layout.c','layout.h','plan.c','plan.h','page002.c','page.h','transaction.h','transaction738.c']:
 a=(old/n.replace('738','737')).read_text().replace('737','738')
 if n=='main.c':a=a.replace('9916,payload_reloc,1,','9916,payload_reloc,10,')
 if n=='page002.c':a=a.replace('count!=1||','count!=10||')
 assert clean(a)==clean((k/n).read_text()),n
b=(k/'bridge.S').read_text();a=(old/'bridge.S').read_text().replace('737','738')
assert a[:a.index('report_offsets:')]==b[:b.index('report_offsets:')]
assert a[a.index('bridge_code_end:'):]==b[b.index('bridge_code_end:'):]
m=json.loads((k/'model001.json').read_text());r=json.loads((k/'integration002.json').read_text());assert m['passed'] and r['passed']
assert len(m['cases'])==56 and len(r['cases'])==53
for c in r['cases']:
 assert c['all_pixels_and_guards_exact']
 assert all(i in [0x1f,0x14,0x17,0x19,0x1b] for i,v in c['CRTC_writes'])
v=next(c['raw_result'] for c in r['cases'] if c['name']=='CR1b85-before-cleanup')
assert v[:8]==[0x7388,0x7388,11,4,14,5,0x85,15] and v[28:31]==[1,1,0]
out=k/'source-review001.json';assert not out.exists()
out.write_text(json.dumps({'passed':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'physical_access':False,'probe_body_matches733_except_namespace_and_native_CPU_guard':True,'frontend_wrapper_unchanged_except_namespace_and_exact10_relocation_count':True,'bridge_changed_only_namespace_and_optical_offsets':True,'model_cases':len(m['cases']),'integration_cases':len(r['cases']),'result_bytes':304,'limits':'No CR22/CR33 data writes, added delay/sample block, mask or repair. Native physical behavior remains unknown; original full704 writes additional registers before checking.'},indent=2)+'\n')
print('PASS738 source delta and compiled safe-prefix contracts')
