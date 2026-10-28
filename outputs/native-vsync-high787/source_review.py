"""Independent787 delta, result layout and execution-evidence review."""
from pathlib import Path
import re,json,datetime,hashlib,struct
K=Path(__file__).resolve().parent;O=K.parent/'native-valid-end785';C=K.parent/'crtc-vsync-high786';P=Path('C:/xwn787/host002')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
def ns(s,a,b):return re.sub(r'(?<![0-9])'+a+r'(?![0-9])',b,re.sub(r'0x'+a+r'(?=[0-9a-f]*\b)','0x'+b,s))
clean=lambda s:re.sub(r'\s+','',re.sub(r'/\*.*?\*/','',s,flags=re.S))
for n in ['probe.c','probe.h']:
 s=ns((C/n).read_text(),'786','787')
 if n=='probe.c':s=s.replace('(o->cr0&0x80000001)!=0x80000001 || (o->cr4&0x20)','(o->cr0&0xe0000001)!=0x40000001 || o->cr3!=0 || (flags&0x200) || (o->cr4&0x20)')
 assert clean(s)==clean((K/n).read_text()),n
old='0,0x8d4,0x5178,0x5290,0x52b0,0x54b4,0x5514,0x5574,0x56dc,0x5754,0x5740,0x574c,0x5750'
new='0,0x8d4,0x50b8,0x51d0,0x51f0,0x53f4,0x5454,0x54b4,0x5694,0x570c,0x56f8,0x5704,0x5708'
for n in ['main.c','layout.c','layout.h','plan.c','plan.h','page002.c','page.h','transaction.h','transaction787.c','bridge.S']:
 s=ns((O/n.replace('787','785')).read_text(),'785','787')
 s=s.replace('15360','16384').replace('0x5100','0x5040').replace('0x57b8','0x5770').replace('0x7b8','0x770').replace(old,new)
 assert clean(s)==clean((K/n).read_text()),n
assert 'frequency!=3375000' in (K/'main.c').read_text()
body=(K/'probe.c').read_text()
positions=[body.index('cw(7,o->c7_before)'),body.index('R32(0x680818)=o->ve_before'),body.index('R32(0x680810)=o->se_before'),body.index('R32(0x68080c)=o->sy_before'),body.index('R32(0x680814)=o->vs_before'),body.index('R32(0x680808)=o->vc_before'),body.index('R32(0x680804)=o->vt_before'),body.index('R32(0x680800)=o->v_before'),body.index('gate(4)')]
assert positions==sorted(positions)
assert not re.search(r'cw\((?:0x1b|0x22|0x33|0x10),',body)
assert read(C/'audit001.json')['passed'] and read(C/'closed001.json')['closed']
m=read(K/'model001.json');r=read(K/'integration004.json')
assert m['passed'] and r['passed'] and len(m['cases'])==575 and len(r['cases'])==565
masks=[30,100,108,121,129,138,148,158,169,181,193,205,221,237,261,285,315,345,375,405,435]
for c in r['cases']:
 assert c['all_pixels_and_guards_exact'] and len(c['raw_result'])==460
 assert all(i in [0,1,2,3,4,5,7,0x1f,0x14,0x17,0x19,0x13] for i,x in c['CRTC_writes'])
for phase in ['before','after','undo']:
 for j in range(9):
  v=next(c['raw_result'] for c in r['cases'] if c['name']=='c7-'+phase+'-'+str(j))
  assert v[0]==(0x78731 if phase=='undo' else 0x78730)
  if phase=='undo':assert v[435]==1<<j and v[101]==0
for j in range(1,9):
 v=next(c['raw_result'] for c in r['cases'] if c['name']=='c7-coupling-'+str(j));assert v[0]==0x78731 and v[435]==1<<j and v[101]==0
for f in ['drop-write','wrong-write','drop-undo','wrong-undo']:
 v=next(c['raw_result'] for c in r['cases'] if c['name']=='c7-'+f);assert v[0]==(0x78731 if f.endswith('undo') else 0x78730)
v=next(c['raw_result'] for c in r['cases'] if c['name']=='prefix-dual')
assert all(v[i]==0 for i in masks) and v[430:436]==[240,116,1,116,240,0]
assert v[436:]==[n for x in [236,96,212,207,207,237,255,16] for n in [x,x,x]]
h=read(K/'host002.json');pages=[];payload=(P/'payload.bin').read_bytes();rawsize=read(K/'payload005.json')['unpadded_bytes']
assert rawsize==15992 and len(payload)==16384 and payload[rawsize:]==b'\xcc'*(16384-rawsize)
for layout in ['dual','identity','relocated','scatter']:
 b=(P/layout/'page.bin').read_bytes();base=struct.unpack_from('<I',b,0x844)[0]
 assert len(b)==32768 and b[0x503c:0x5770]==bytes(0x734)
 assert b[0x5770:0x5800]==b'\xa5'*0x90 and b[0x6000:]==b'\xa5'*0x2000
 assert struct.unpack_from('<HI',b,0x830)==(2047,base+0x5800)
 target=base+h['bridge_symbols']['bridge_fault']
 for i in range(256):assert struct.unpack_from('<4H',b,0x5800+8*i)==(target&65535,0x10,0x8e00,target>>16)
 expected=bytearray(payload)
 for x in h['relocations']:
  if x['type']=='R_386_32':struct.pack_into('<I',expected,x['offset'],x['value']+base+0x1000-0x100000)
 assert b[0x1000:0x5000]==expected
 checksum=sum(struct.unpack_from('<I',b,i)[0] for i in range(0,0x6000,4) if i!=0x854 and not 0x880<=i<0x900)&0xffffffff
 assert struct.unpack_from('<I',b,0x854)[0]==checksum
 assert 0x1000+16384==0x5000<0x503c<0x5040 and 0x5040+460*4==0x5770<0x5800 and 0x5800+256*8==0x6000
 pages.append({'layout':layout,'sha256':sha(P/layout/'page.bin'),'payload':[0x1000,0x5000],'request':[0x5000,0x503c],'request_guard':[0x503c,0x5040],'result':[0x5040,0x5770],'result_guard':[0x5770,0x5800],'IDT':[0x5800,0x6000],'stack':[0x6000,0x8000],'all256IDTentries_exact':True,'relocated_payload_and_checksum_exact':True})
offsets=[int(n,0) for n in new.split(',')];b=(P/'bridge.bin').read_bytes()
assert list(struct.unpack_from('<13I',b,h['bridge_symbols']['report_offsets']))==offsets
names=['signature','return_code','prefix_cleanup_mask','horizontal_cleanup_mask','CRTC_cleanup_mask','vertical_display_end_cleanup_mask','vertical_total_cleanup_mask','vertical_crtc_cleanup_mask','vertical_valid_end_cleanup_mask','CR07_cleanup_mask','CR07_before','CR07_after','CR07_restored']
omitted=['CR00','CR02','CR03','secondCR05','firstCR17','CR01','secondCR02','secondCR17','secondCR19','CR13','NVVVALIDSTART','NVVSYNCSTART','NVVSYNCEND']
schema={'passed':True,'rows':13,'columns':32,'offsets':offsets,'names':names,'bit_order':'MSB left white1 black0 gray background','omitted_aggregate_masks':omitted,'total_masks_required_for_success':21,'target_CR07':116,'limitations':'Same-value CR02/NVVVALIDSTART drops indistinguishable. Thirteen masks and neighbor/CPU/selector raw values omitted; final787 requires all21 clear. No native disk/fullmode/Windows proof.'}
for n,obj in [('optical-schema001.json',schema),('layout-independent001.json',{'passed':True,'physical_access':False,'checks':pages,'payload_IDT_result_stack_disjoint':True}),('source-review001.json',{'passed':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'physical_access':False,'probe_matches786_except_namespace_native_CPU_guard':True,'frontend_matches785_except_namespace_report_offsets_and_reviewed_layout_changes':True,'result_bytes':1840,'result_end_offset':0x5770,'page_bounds':pages,'model_cases':575,'integration_cases':565,'failed_recovery_inhibits_output':True,'kernel_audit_sha256':sha(C/'audit001.json')})]:
 assert not (K/n).exists();(K/n).write_text(json.dumps(obj,indent=2)+'\n')
print('PASS787 source, all execution cases and exact independently checked memory layout')
