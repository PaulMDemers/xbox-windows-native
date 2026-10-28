"""Independent786 source, target, linked bytes, fault schema and recovery review."""
from pathlib import Path
import ast,datetime,hashlib,json,re
from audit_logic import validate
K=Path(__file__).resolve().parent;O=K.parent/'vertical-valid-end784';P=Path('C:/xwn786/build001')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
def ns(s):return s.replace('784','786').replace('vertical-valid-end786','crtc-vsync-high786')
def save(n,r):
 with (K/n).open('x') as f:json.dump(r,f,indent=2);f.write('\n')
r={'passed':False,'reviewer_sha256':sha(Path(__file__))};assert not (K/'review003.json').exists()
try:
 for f in K.glob('*.py'):ast.parse(f.read_text())
 d=read(K/'delta001.json');body=(K/'probe.c').read_text();stripped=body
 for token in [d['init'],d['block'],d['undo'],' && !o->c7_cleanup_mask',' if(o->c7_cleanup_mask)o->code=0x78631;\n']:
  assert stripped.count(token)==1;stripped=stripped.replace(token,'')
 assert stripped==ns((O/'probe.c').read_text())
 fields=['c7_before','c7_target','c7_attempted','c7_after','c7_restored','c7_cleanup_mask']
 for n in ['c7_c6','c7_c9','c7_c10','c7_c12','c7_c15','c7_c16','c7_c18','c7_c25']:fields += [n+'_before',n+'_after',n+'_restored']
 assert d['fields']==fields and len(fields)==30
 assert (K/'probe.h').read_text().replace(' uint32_t '+','.join(fields)+';\n','')==ns((O/'probe.h').read_text())
 expected=ns((O/'main.c').read_text()).replace('words[430]','words[460]').replace('i<430','i<460').replace('vertical_valid_end_control','crtc_vsync_high_control').replace('result.ve_cleanup_mask){','result.ve_cleanup_mask || result.c7_cleanup_mask){').replace('result.code==0x7862e)','result.code==0x7862e || result.code==0x78630)')
 assert (K/'main.c').read_text()==expected
 assert (K/'Makefile').read_text()==ns((O/'Makefile').read_text()).replace('NVVVALIDEND','CR07 VSYNC HIGH')
 for n in ['layout.c','layout.h']:assert (K/n).read_bytes()==(O/n).read_bytes()
 legacy=K.parent/'xcal-transaction704/gpu_legacy.c';assert sha(legacy)=='5e686c6e875f9d9bb60a0955bedfb4978911f5a79bf1feaea47080d9d7fe5690'
 source=re.sub(r'\s+','',legacy.read_text());i=source.index('//CRTC_VSYNCSTART');snippet=source[i:i+500]
 assert 'b=NvGetCrtc(pbRegs,7)&0x7b;' in snippet
 assert 'NvSetCrtc(pbRegs,7,b|((gpu->crtcvstart>>2)&0x80)|((gpu->crtcvstart>>6)&0x04));' in snippet
 assert snippet.index('NvSetCrtc(pbRegs,7,')<snippet.index('NvSetCrtc(pbRegs,0x10,')
 target=K.parent/'xcal-transaction704/transaction003.c';types=K.parent/'xcal-transaction704/gpu_types.h'
 assert '{720,720,738,779,480,489,489,524,524,4,3}' in target.read_text().replace(' ','')
 assert re.findall(r'long\s+(\w+);',types.read_text())[:9]==['xres','crtchdispend','nvhstart','nvhtotal','yres','nvvstart','crtcvstart','crtcvtotal','nvvtotal']
 assert (0xf0&0x7b)|((489>>2)&0x80)|((489>>6)&4)==0x74
 assert (0xf0^0x74)==0x84 and (0xf0&0x7b)==(0x74&0x7b)
 prior=read(O/'audit002.json');assert prior['passed'] and read(O/'closed001.json')['closed']
 assert [prior['result']['vertical_valid_end'][n] for n in ['before','after','restored']]==[719,479,719]
 native=K.parent/'native-valid-end785';assert read(native/'closed001.json')['closed'] and read(native/'audit006.json')['passed']
 crtc=next(v['data']['crtc_kernel_reads'] for v in read(O/'collection001.json')['reports'].values() if v['data'].get('crtc_kernel_reads'))
 r['retained_crtc_reads']=crtc
 assert [dict(crtc)[i] for i in [7,6,9,16,18,21,22,24,37]]==[240,236,96,212,207,207,237,255,16]
 for a in ['800','804','808','814','80c','810','818']:assert body.count('R32(0x680'+a+')=')==2
 assert body.count('cw(7,')==2 and not re.search(r'cw\((?:0x1b|0x22|0x33|0x07|0x10),',body)
 order=['cw(7,o->c7_before)','R32(0x680818)=o->ve_before','R32(0x680810)=o->se_before','R32(0x68080c)=o->sy_before','R32(0x680814)=o->vs_before','R32(0x680808)=o->vc_before','R32(0x680804)=o->vt_before','R32(0x680800)=o->v_before','gate(4)']
 assert [body.index(t) for t in order]==sorted(body.index(t) for t in order)
 assert 'o->c7_target=(o->c7_before&0x7bu)|((489u>>2)&0x80u)|((489u>>6)&4u);' in body
 assert d['neighbors']==[['c7_c6',6,236],['c7_c9',9,96],['c7_c10',16,212],['c7_c12',18,207],['c7_c15',21,207],['c7_c16',22,237],['c7_c18',24,255],['c7_c25',37,16]]
 for n,a,v in d['neighbors']:
  assert 'o->'+n+'_before!='+hex(v) in d['block']
  assert 'o->'+n+'_after!=o->'+n+'_before' in d['block'] and 'o->'+n+'_restored!=o->'+n+'_before' in d['undo']
 for n in ['main.c','layout.c','layout.h','probe.c','probe.h','Makefile']:assert sha(K/n)==sha(P/n)
 model=read(K/'model001.json');cases=model['cases'];assert model['passed'] and len(cases)==575
 for c in cases:validate(c['raw_result'])
 assert len(read(K/'clock-model001.json')['cases'])==10 and read(K/'layout-model001.json')['case_count']==2353
 mutations=[];base=cases[0]['raw_result']
 for i in [0,1,28,30,83,90,97,98,100,101]+list(range(104,460)):
  v=base.copy();v[i]^=1
  try:validate(v)
  except AssertionError:mutations.append(i)
  else:raise AssertionError(('accepted mutation',i))
 for c in cases:
  if c['raw_result'][435]:
   assert c['raw_result'][0]==0x78631 and c['raw_result'][101]==0 and c['ports']==[5]
   v=c['raw_result'].copy();v[101]=1
   try:validate(v)
   except AssertionError:mutations.append(c['name'])
   else:raise AssertionError('unsafe output enable admitted')
 assert base[430:]==[240,116,1,116,240,0]+[a for n in [236,96,212,207,207,237,255,16] for a in [n]*3]
 assert [v for v in cases[0]['writes'] if v[0]=='cr' and v[1]==7]==[['cr',7,116],['cr',7,240]]
 assert next(c for c in cases if c['name']=='c7-drop-write')['raw_result'][0]==0x78630
 assert next(c for c in cases if c['name']=='c7-drop-undo')['raw_result'][0]==0x78631
 checks=['build001.json','model001.json','layout-model001.json','clock-model001.json','link-review001.json','layout-link-review001.json','main-link-review001.json']
 assert all(read(K/n)['passed'] for n in checks)
 save('schema001.json',{'words':460,'bytes':1840,'inherited':'0..429 same784; namespace786','new_fields':dict(zip(fields,range(430,460))),'new_statuses':{'78630':'baseline/forward/neighbor mismatch','78631':'own or neighbor recovery mismatch; output inhibited'},'target':116,'baseline':240,'native_end_if_offset5100':0x5830,'native_requires_fresh_bounds_proof':True,'native_warning':'Would overlap785 IDT beginning5800; no native reuse without fresh layout qualification'})
 save('source-review001.json',{'passed':True,'legacy_sha256':sha(legacy),'target_source_sha256':sha(target),'target_types_sha256':sha(types),'target_derivation':'crtcvstart489: first CR07 write only, mask84; baselineF0->74->F0. CR10 remainsD4.','retained_kernel_sha256':sha(O/'audit002.json'),'retained_native_closure_sha256':sha(native/'closed001.json'),'prior_source_exact_after_removing_delta':True,'own_reverse_recovery':True,'all_575_schema_cases_pass':True,'rejected_schema_mutations':mutations,'scope':'host access/control-flow only; no physical semantics proof'})
 checks+=['schema001.json','source-review001.json','lineage001.json','delta001.json','clock-lineage001.json']
 r.update(passed=True,checks={n:sha(K/n) for n in checks},model_cases=575,layout_cases=2353,max_modeled_critical_instructions=max(c['critical_instructions'] for c in cases),physical_proof=False)
 save('sources001.json',{f.name:sha(f) for f in K.iterdir() if f.suffix in ['.c','.h','.py'] or f.name in ['Makefile','.gitattributes']})
except BaseException as e:r['failure']=repr(e);raise
finally:r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save('review003.json',r)
print('PASS786 independent source/schema/build review')
