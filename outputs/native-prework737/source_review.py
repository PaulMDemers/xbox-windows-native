from pathlib import Path
import re,json,hashlib,datetime
k=Path('outputs/native-prework737');old=Path('outputs/native-interaction727')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
clean=lambda s:re.sub(r'\s+','',re.sub(r'/\*.*?\*/','',s,flags=re.S))
for n in ['main.c','layout.c','layout.h','plan.c','plan.h','page002.c','page.h','transaction.h','transaction737.c']:
 p=old/n.replace('737','727')
 assert clean(p.read_text().replace('727','737'))==clean((k/n).read_text()),n
a=(old/'bridge.S').read_text().replace('727','737');b=(k/'bridge.S').read_text()
assert a[:a.index('report_offsets:')]==b[:b.index('report_offsets:')]
assert a[a.index('bridge_code_end:'):]==b[b.index('bridge_code_end:'):]
a=(old/'probe.c').read_text().replace('727','737');b=(k/'probe.c').read_text()
start=b.index(' {uint32_t count=4093,sum=0x13579bdf;');end=b.index(' o->direct=',start)
loop=b[start:end]
assert 'roll $1,%0; xorl $0x9e3779b9,%0; decl %1; jnz 1b' in loop
assert not any(v in loop for v in ['R8(','R32(','cw(','cr(','gate('])
without=b[:start]+b[end:]
extra='((o->work_iterations==4093 && o->work_counter_end==0 && o->work_checksum==0x793a7efe)?8u:0u)|'
assert without.count(extra)==1
assert clean(a)==clean(without.replace(extra,''))
a=(old/'probe.h').read_text().replace('727','737');b=(k/'probe.h').read_text()
assert clean(a)==clean(b.replace(' uint32_t work_iterations,work_counter_end,work_checksum;',''))
run=json.loads((k/'integration002.json').read_text());assert run['passed'] and len(run['cases'])==51
for c in run['cases']:
 assert c['all_pixels_and_guards_exact']
 assert c['MMIO_writes'] in ([],[[0x680630,2],[0x680630,3]])
 assert c['CRTC_data_writes'] in ([],[[0x1f,0x57]],[[0x1f,0x57],[0x1b,5]])
 if [0x1b,5] in c['CRTC_data_writes']:
  assert c['direct_indexed_access_order_exact'] and c['cpu_only_work']['iterations']==4093 and c['cpu_only_work']['ended']
v={c['name']:c['raw_result'] for c in run['cases']}
assert v['reassert-dual'][50:53]==[5,5,0x50005]
assert v['behavior-after-work'][50:53]==[0x85,0x85,0x850085]
assert v['behavior-after-work'][0]==0x7378 and v['behavior-after-work'][18:20]==[1,1]
assert v['behavior-sticky'][0]==0x7375 and v['behavior-sticky'][29:32]==[5,5,5]
assert v['behavior-direct-diff'][50:53]==[0x85,5,0x850005]
r={'passed':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'physical_access':False,'source_delta_from727':'Only fixed4093 CPU-register loop and three appended result words plus work-complete summary bit; bridge report offsets and namespace. Frontend/page/ownership/context wrapper unchanged.','device_access_sequence_same':True,'no_CR1b_mask_retry_or_repair':True,'compiled_work_iteration_and_no_device_access_checks':True,'result_bytes':228,'integration_cases':51,'limits':'Scripted after-work readback is a model, not hardware timing/bit7 semantics. Native minimal727 sequence differs from larger kernel735/736 prefix.'}
out=k/'source-review001.json';assert not out.exists();out.write_text(json.dumps(r,indent=2)+'\n')
print('PASS737 exact source delta, compiled loop and device access restrictions')
