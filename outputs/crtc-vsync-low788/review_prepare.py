"""Independent788 source, target, linked bytes, full fault schema and recovery review."""
from pathlib import Path
import ast,datetime,hashlib,json,re
from audit_logic import validate
K=Path(__file__).resolve().parent;O=K.parent/'crtc-vsync-high786';P=Path('C:/xwn788/build001')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
def ns(s):return s.replace('786','788').replace('crtc-vsync-high788','crtc-vsync-low788')
def save(n,r):
 with (K/n).open('x') as f:json.dump(r,f,indent=2);f.write('\n')
r={'passed':False,'reviewer_sha256':sha(Path(__file__))};assert not (K/'review001.json').exists()
try:
 for f in K.glob('*.py'):ast.parse(f.read_text())
 d=read(K/'delta001.json');body=(K/'probe.c').read_text();stripped=body
 for token in [d['init'],d['block'],d['undo'],' && !o->c10_cleanup_mask',' if(o->c10_cleanup_mask)o->code=0x78833;\n']:
  assert stripped.count(token)==1;stripped=stripped.replace(token,'')
 assert stripped==ns((O/'probe.c').read_text())
 fields=['c10_before','c10_target','c10_attempted','c10_after','c10_restored','c10_cleanup_mask']
 for n in ['c10_c6','c10_c7','c10_c9','c10_c12','c10_c15','c10_c16','c10_c18','c10_c25']:fields += [n+'_before',n+'_after',n+'_restored']
 assert d['fields']==fields and len(fields)==30
 assert (K/'probe.h').read_text().replace(' uint32_t '+','.join(fields)+';\n','')==ns((O/'probe.h').read_text())
 expected=ns((O/'main.c').read_text()).replace('words[460]','words[490]').replace('i<460','i<490').replace('crtc_vsync_high_control','crtc_vsync_low_control').replace('result.c7_cleanup_mask){','result.c7_cleanup_mask || result.c10_cleanup_mask){').replace('result.code==0x78830)','result.code==0x78830 || result.code==0x78832)')
 assert (K/'main.c').read_text()==expected
 assert (K/'Makefile').read_text()==ns((O/'Makefile').read_text()).replace('CR07 VSYNC HIGH','CR10 VSYNC LOW')
 for n in ['layout.c','layout.h']:assert (K/n).read_bytes()==(O/n).read_bytes()
 legacy=K.parent/'xcal-transaction704/gpu_legacy.c';assert sha(legacy)=='5e686c6e875f9d9bb60a0955bedfb4978911f5a79bf1feaea47080d9d7fe5690'
 source=re.sub(r'\s+','',legacy.read_text());i=source.index('//CRTC_VSYNCSTART');snippet=source[i:i+500]
 assert snippet.index('NvSetCrtc(pbRegs,7,')<snippet.index('NvSetCrtc(pbRegs,0x10,(gpu->crtcvstart&0xff));')<snippet.index('//CRTC_VTOTAL')
 target=K.parent/'xcal-transaction704/transaction003.c';types=K.parent/'xcal-transaction704/gpu_types.h'
 assert '{720,720,738,779,480,489,489,524,524,4,3}' in target.read_text().replace(' ','')
 assert re.findall(r'long\s+(\w+);',types.read_text())[:9]==['xres','crtchdispend','nvhstart','nvhtotal','yres','nvvstart','crtcvstart','crtcvtotal','nvvtotal']
 assert 489&255==233 and 724&255==212
 prior=read(O/'audit001.json');assert prior['passed'] and read(O/'closed001.json')['closed']
 assert [prior['result']['crtc_vsync_high'][n] for n in ['before','after','restored']]==[240,116,240]
 native=K.parent/'native-vsync-high787';assert read(native/'closure001.json')['closed'] and read(native/'audit006.json')['passed']
 crtc=next(v['data']['crtc_kernel_reads'] for v in read(O/'collection001.json')['reports'].values() if v['data'].get('crtc_kernel_reads'))
 r['retained_crtc_reads']=crtc
 assert [dict(crtc)[i] for i in [16,6,7,9,18,21,22,24,37]]==[212,236,240,96,207,207,237,255,16]
 for a in ['800','804','808','814','80c','810','818']:assert body.count('R32(0x680'+a+')=')==2
 assert body.count('cw(7,')==2 and body.count('cw(0x10,')==2
 assert not re.search(r'cw\((?:0x1b|0x22|0x33|0x07|0x06|6|0x16),',body)
 order=['cw(7,o->c7_target)','cw(0x10,o->c10_target)','cw(0x10,o->c10_before)','cw(7,o->c7_before)','R32(0x680818)=o->ve_before','R32(0x680810)=o->se_before','R32(0x68080c)=o->sy_before','R32(0x680814)=o->vs_before','R32(0x680808)=o->vc_before','R32(0x680804)=o->vt_before','R32(0x680800)=o->v_before','gate(4)']
 assert [body.index(t) for t in order]==sorted(body.index(t) for t in order)
 assert 'o->c10_target=489u&0xffu;' in body
 assert d['neighbors']==[['c10_c6',6,236],['c10_c7',7,116],['c10_c9',9,96],['c10_c12',18,207],['c10_c15',21,207],['c10_c16',22,237],['c10_c18',24,255],['c10_c25',37,16]]
 for n,a,v in d['neighbors']:
  assert 'o->'+n+'_before!='+hex(v) in d['block']
  assert 'o->'+n+'_after!=o->'+n+'_before' in d['block'] and 'o->'+n+'_restored!=o->'+n+'_before' in d['undo']
 for n in ['main.c','layout.c','layout.h','probe.c','probe.h','Makefile']:assert sha(K/n)==sha(P/n)
 model=read(K/'model001.json');cases=model['cases'];assert model['passed'] and len(cases)==614
 for c in cases:validate(c['raw_result'])
 assert len(read(K/'clock-model001.json')['cases'])==10 and read(K/'layout-model001.json')['case_count']==2353
 mutations=[];base=cases[0]['raw_result']
 for i in [0,1,28,30,83,90,97,98,100,101]+list(range(104,490)):
  v=base.copy();v[i]^=1
  try:validate(v)
  except AssertionError:mutations.append(i)
  else:raise AssertionError(('accepted mutation',i))
 for c in cases:
  if c['raw_result'][465]:
   assert c['raw_result'][0]==0x78833 and c['raw_result'][101]==0 and c['ports']==[5]
   v=c['raw_result'].copy();v[101]=1
   try:validate(v)
   except AssertionError:mutations.append(c['name'])
   else:raise AssertionError('unsafe output enable admitted')
 assert base[460:]==[212,233,1,233,212,0]+[a for n in [236,116,96,207,207,237,255,16] for a in [n]*3]
 assert [v for v in cases[0]['writes'] if v[0]=='cr' and v[1] in [7,16]]==[['cr',7,116],['cr',16,233],['cr',16,212],['cr',7,240]]
 byname={c['name']:c for c in cases}
 assert byname['c10-drop-write']['raw_result'][0]==0x78832
 assert byname['c10-drop-undo']['raw_result'][0]==0x78833
 assert byname['c10-drop-undo']['raw_result'][435]==8
 assert byname['c10-coupling-2']['raw_result'][465]==4 and byname['c10-coupling-2']['raw_result'][435]==0
 for j,m in [(1,2),(3,4),(4,16),(5,32),(6,64),(7,128),(8,256)]:assert byname['c10-coupling-'+str(j)]['raw_result'][435]==m
 checks=['build001.json','model001.json','layout-model001.json','clock-model001.json','link-review001.json','layout-link-review001.json','main-link-review001.json']
 assert all(read(K/n)['passed'] for n in checks)
 save('schema001.json',{'words':490,'bytes':1960,'inherited':'0..459 same786; namespace788','new_fields':dict(zip(fields,range(460,490))),'new_statuses':{'78832':'baseline/forward/neighbor mismatch','78833':'own or neighbor recovery mismatch; output inhibited'},'target':233,'baseline':212,'native_requires_fresh_bounds_proof':True,'native_warning':'No native payload created/admitted; prior787 only392 executable bytes free, proposed490word result at5040 leaves24bytes before IDT5800'})
 save('source-review001.json',{'passed':True,'legacy_sha256':sha(legacy),'target_source_sha256':sha(target),'target_types_sha256':sha(types),'target_derivation':'crtcvstart489 low byte E9 after CR07=74; retained720p CR10 D4; CR10 reverse before CR07.','retained_kernel_sha256':sha(O/'audit001.json'),'retained_native_closure_sha256':sha(native/'closure001.json'),'prior_source_exact_after_removing_delta':True,'own_reverse_recovery':True,'all_614_schema_cases_pass':True,'rejected_schema_mutations':mutations,'scope':'host access/control-flow only; no physical semantics proof'})
 checks+=['schema001.json','source-review001.json','lineage001.json','delta001.json','clock-lineage001.json','preparation-failure001.json']
 r.update(passed=True,checks={n:sha(K/n) for n in checks},model_cases=614,layout_cases=2353,max_modeled_critical_instructions=max(c['critical_instructions'] for c in cases),physical_proof=False)
 save('sources001.json',{f.name:sha(f) for f in K.iterdir() if f.suffix in ['.c','.h','.py'] or f.name in ['Makefile','.gitattributes']})
except BaseException as e:r['failure']=repr(e);raise
finally:r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save('review001.json',r)
print('PASS788 independent source/schema/build review')
