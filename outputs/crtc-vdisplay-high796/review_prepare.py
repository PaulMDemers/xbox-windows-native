"""Independent source-delta, target, compiled evidence and result-schema review."""
from pathlib import Path
import ast,datetime,hashlib,json,re
from audit_logic import validate
K=Path(__file__).resolve().parent;O=K.parent/'crtc-vblank-end794';P=Path('C:/xwn796/build001')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
def ns(s):return s.replace('794','796').replace('crtc-vblank-end796','crtc-vdisplay-high796')
def save(n,r):
 with (K/n).open('x') as f:json.dump(r,f,indent=2);f.write('\n')
r={'passed':False,'reviewer_sha256':sha(Path(__file__))};assert not (K/'review001.json').exists()
try:
 for f in K.glob('*.py'):ast.parse(f.read_text())
 d=read(K/'delta001.json');body=(K/'probe.c').read_text();stripped=body
 for token in [d['init'],d['block'],d['undo'],' && !o->cd7_cleanup_mask',' if(o->cd7_cleanup_mask)o->code=0x7963b;\n']:
  assert stripped.count(token)==1;stripped=stripped.replace(token,'')
 assert stripped==ns((O/'probe.c').read_text())
 fields=['cd7_before','cd7_target','cd7_attempted','cd7_after','cd7_restored','cd7_cleanup_mask']
 for n in ['cd7_c6','cd7_c9','cd7_c10','cd7_c12','cd7_c15','cd7_c16','cd7_c18','cd7_c25']:fields += [n+'_before',n+'_after',n+'_restored']
 assert fields==d['fields'] and len(fields)==30
 assert (K/'probe.h').read_text().replace(' uint32_t '+','.join(fields)+';\n','')==ns((O/'probe.h').read_text())
 expected=ns((O/'main.c').read_text()).replace('words[580]','words[610]').replace('i<580','i<610').replace('crtc_vblank_end_control','crtc_vdisplay_high_control').replace('result.ct16_cleanup_mask){','result.ct16_cleanup_mask || result.cd7_cleanup_mask){').replace('result.code==0x79638)','result.code==0x79638 || result.code==0x7963a)')
 assert (K/'main.c').read_text()==expected
 assert (K/'Makefile').read_text()==ns((O/'Makefile').read_text()).replace('CR16 VBLANK END','CR07 VDISPLAY HIGH')
 for n in ['layout.c','layout.h']:assert (K/n).read_bytes()==(O/n).read_bytes()
 legacy=K.parent/'xcal-transaction704/gpu_legacy.c';assert sha(legacy)=='5e686c6e875f9d9bb60a0955bedfb4978911f5a79bf1feaea47080d9d7fe5690'
 source=re.sub(r'\s+','',legacy.read_text());a=source.index('//CRTC_VDISPEND');snippet=source[a:source.index('NvSetCrtc(pbRegs,0x12',a)]
 assert 'b=NvGetCrtc(pbRegs,7)&0xbd;' in snippet
 assert 'NvSetCrtc(pbRegs,7,b|(((gpu->yres-1)>>3)&0x40)|(((gpu->yres-1)>>7)&0x02));' in snippet
 target=K.parent/'xcal-transaction704/transaction003.c';types=K.parent/'xcal-transaction704/gpu_types.h'
 assert '{720,720,738,779,480,489,489,524,524,4,3}' in target.read_text().replace(' ','')
 assert re.findall(r'long\s+(\w+);',types.read_text())[:9]==['xres','crtchdispend','nvhstart','nvhtotal','yres','nvvstart','crtcvstart','crtcvtotal','nvvtotal']
 assert ((116&0xbd)|((479>>3)&0x40)|((479>>7)&2))==54
 prior=read(O/'audit002.json');assert prior['passed'] and read(O/'closed001.json')['closed']
 assert [prior['result']['crtc_vblank_end'][n] for n in ['before','after','restored']]==[237,140,237]
 native=K.parent/'native-vblank-end795';assert read(native/'closed001.json')['closed'] and read(native/'audit001.json')['passed']
 assert not re.search(r'cw\((?:0x1b|0x22|0x33|0x12),',body)
 order=['cw(7,o->c7_target)','cw(0x10,o->c10_target)','cw(7,o->ct7_target)','cw(6,o->ct6_target)','cw(0x16,o->ct16_target)','cw(7,o->cd7_target)','cw(7,o->cd7_before)','cw(0x16,o->ct16_before)','cw(6,o->ct6_before)','cw(7,o->ct7_before)','cw(0x10,o->c10_before)','cw(7,o->c7_before)','gate(4)']
 assert [body.index(t) for t in order]==sorted(body.index(t) for t in order)
 assert 'o->cd7_target=(o->cd7_before&0xbdu)|(((480u-1u)>>3)&0x40u)|(((480u-1u)>>7)&0x02u);' in body
 assert d['neighbors']==[['cd7_c6',6,12],['cd7_c9',9,96],['cd7_c10',16,233],['cd7_c12',18,207],['cd7_c15',21,207],['cd7_c16',22,140],['cd7_c18',24,255],['cd7_c25',37,16]]
 for n,a,v in d['neighbors']:
  assert 'o->'+n+'_before!='+hex(v) in d['block']
  assert 'o->'+n+'_after!=o->'+n+'_before' in d['block'] and 'o->'+n+'_restored!=o->'+n+'_before' in d['undo']
 for n in ['main.c','layout.c','layout.h','probe.c','probe.h','Makefile']:assert sha(K/n)==sha(P/n)
 model=read(K/'model002.json');cases=model['cases'];assert model['passed'] and len(cases)==774
 for c in cases:
  try:validate(c['raw_result'])
  except AssertionError:raise AssertionError(('schema',c['name']))
 assert len(read(K/'clock-model001.json')['cases'])==10 and read(K/'layout-model001.json')['case_count']==2353
 mutations=[];base=cases[0]['raw_result']
 for i in [0,1,28,30,83,90,97,98,100,101]+list(range(104,610)):
  v=base.copy();v[i]^=1
  try:validate(v)
  except AssertionError:mutations.append(i)
  else:raise AssertionError(('accepted mutation',i))
 for c in cases:
  if c['raw_result'][585]:
   assert c['raw_result'][0]==0x7963b and c['raw_result'][101]==0 and c['ports']==[5]
   v=c['raw_result'].copy();v[101]=1
   try:validate(v)
   except AssertionError:mutations.append(c['name'])
   else:raise AssertionError('unsafe output enable admitted')
 assert base[580:]==[116,54,1,54,116,0]+[a for n in [12,96,233,207,207,140,255,16] for a in [n]*3]
 byname={c['name']:c for c in cases}
 assert byname['cd7-drop-write']['raw_result'][1]==0x7963a
 for n in ['cd7-drop-undo','cd7-wrong-undo','cd7-wrong-write-drop-undo']:
  v=byname[n]['raw_result'];assert [v[i] for i in [585,555,525,495,465,435]]==[1,4,2,0,0,0]
 for j,m in [(1,[2,2,0,0,0,0]),(2,[4,8,4,4,8,4]),(3,[8,16,8,8,0,0]),(6,[64,0,0,0,0,0])]:
  assert [byname['cd7-coupling-'+str(j)]['raw_result'][i] for i in [585,555,525,495,465,435]]==m
 checks=['build001.json','model002.json','layout-model001.json','clock-model001.json','link-review001.json','layout-link-review001.json','main-link-review001.json']
 assert all(read(K/n)['passed'] for n in checks)
 save('schema001.json',{'words':610,'bytes':2440,'inherited':'0..579 same794; namespace796','new_fields':dict(zip(fields,range(580,610))),'new_statuses':{'7963a':'baseline/forward/neighbor mismatch','7963b':'own or neighbor recovery mismatch; output inhibited'},'target':54,'baseline':116,'native_requires_fresh_bounds_proof':True})
 save('source-review001.json',{'passed':True,'legacy_sha256':sha(legacy),'target_source_sha256':sha(target),'target_types_sha256':sha(types),'target_derivation':'(saved74 &BD)|(((480-1)>>3)&40)|(((480-1)>>7)&02)=36 after CR16=8C. Third CR07 restored before CR16.','retained_kernel_sha256':sha(O/'audit002.json'),'retained_native_closure_sha256':sha(native/'closed001.json'),'prior_source_exact_after_removing_delta':True,'own_reverse_recovery':True,'all_774_schema_cases_pass':True,'rejected_schema_mutations':mutations,'scope':'host access/control-flow only; no physical semantics proof'})
 checks+=['schema001.json','source-review001.json','lineage001.json','delta001.json','clock-lineage001.json','qualification-failure001.json']
 r.update(passed=True,checks={n:sha(K/n) for n in checks},model_cases=774,layout_cases=2353,max_modeled_critical_instructions=max(c['critical_instructions'] for c in cases),physical_proof=False)
 save('sources001.json',{f.name:sha(f) for f in K.iterdir() if f.suffix in ['.c','.h','.py'] or f.name in ['Makefile','.gitattributes']})
except BaseException as e:r['failure']=repr(e);raise
finally:r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save('review001.json',r)
print('PASS796 independent source/schema/build review')
