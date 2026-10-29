"""Independent807 source delta, actual compiled admission and full schema review."""
from pathlib import Path
import ast,datetime,hashlib,json,re
K=Path(__file__).resolve().parent;O=K.parent/'crtc-vblank-low805';P=Path('C:/xwn807/build002')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
def ns(s):
 parts=re.split(r'(0x[0-9a-fA-F]+)',s)
 return ''.join(re.sub(r'^0x805(?=[0-9a-f]{0,2}$)','0x807',p) if i%2 else p.replace('805','807') for i,p in enumerate(parts)).replace('crtc-vblank-low807','crtc-linecompare-high807')
def save(n,r):
 with (K/n).open('x') as f:json.dump(r,f,indent=2);f.write('\n')
compact=lambda s:re.sub(r'\s+','',s)
r=dict(passed=False,reviewer_sha256=sha(Path(__file__)));assert not (K/'review003.json').exists()
try:
 assert read(O/'closed001.json')['closed'] and read(O/'closed001.json')['passed']
 for p in K.glob('*.py'):ast.parse(p.read_text())
 for n in ['probe.c','probe.h','main.c','layout.c','layout.h','Makefile']:assert sha(K/n)==sha(P/n),n
 for n in ['layout.c','layout.h','prefix_schema.py']:assert (K/n).read_text()==ns((O/n).read_text()),n
 probe=(K/'probe.c').read_text();old=ns((O/'probe.c').read_text())
 start=probe.index(' /* CRTC_LINECOMP high bit, pinned704 m=0x3ff; same-value at this baseline. */')
 end=probe.index(' o->forward_status=0x807;\nrestore:',start)
 forward=probe[start:end];body=forward[forward.index('o->forward_status='):]
 regs=[6,9,16,18,21,22,24,37];values=[12,64,233,223,223,140,255,16]
 labels=['cl7_c6','cl7_c9','cl7_c10','cl7_c12','cl7_c15','cl7_c16','cl7_c18','cl7_c25']
 expected='o->forward_status=0x80744;o->cl7_before=cr(7);'
 expected+=''.join(f'o->{n}_before=cr({hex(a)});' for n,a in zip(labels,regs))
 expected+='if(o->cl7_before!=0x3e||'+'||'.join(f'o->{n}_before!={hex(v)}' for n,v in zip(labels,values))+')goto restore;'
 expected+='o->cl7_target=(o->cl7_before&0xefu)|((0x3ffu>>4)&0x10u);o->cl7_attempted=1;cw(7,o->cl7_target);o->cl7_after=cr(7);'
 expected+=''.join(f'o->{n}_after=cr({hex(a)});' for n,a in zip(labels,regs))
 expected+='if(o->cl7_after!=o->cl7_target||'+'||'.join(f'o->{n}_after!=o->{n}_before' for n in labels)+')goto restore;'
 assert compact(body)==compact(expected)
 undo=next(line+'\n' for line in probe.splitlines() if line.startswith(' if(o->cl7_attempted){'))
 expected='if(o->cl7_attempted){cw(7,o->cl7_before);o->cl7_restored=cr(7);'
 expected+=''.join(f'o->{n}_restored=cr({hex(a)});' for n,a in zip(labels,regs))
 expected+='if(o->cl7_restored!=o->cl7_before)o->cl7_cleanup_mask|=1;'
 expected+=''.join(f'if(o->{n}_restored!=o->{n}_before)o->cl7_cleanup_mask|={2<<i};' for i,n in enumerate(labels))+'}'
 assert compact(undo)==compact(expected) and probe.index(undo)<probe.index(' if(o->cb15_attempted){')
 init=next(line+'\n' for line in probe.splitlines() if line.startswith(' o->cl7_after=0xffffffff;'))
 fields=['cl7_before','cl7_target','cl7_attempted','cl7_after','cl7_restored','cl7_cleanup_mask']
 for n in labels:fields.extend([n+'_before',n+'_after',n+'_restored'])
 assert compact(init)==''.join(f'o->{f}=0xffffffff;' for f in fields if f.endswith(('_after','_restored')))
 stripped=probe.replace(forward,'').replace(undo,'').replace(init,'').replace(' && !o->cl7_cleanup_mask','').replace(' if(o->cl7_cleanup_mask)o->code=0x80745;\n','')
 assert stripped==old,'unapproved prefix/source change'
 assert (K/'probe.h').read_text()==ns((O/'probe.h').read_text()).replace('};',' uint32_t '+','.join(fields)+';\n};')
 main=(K/'main.c').read_text();expected=ns((O/'main.c').read_text()).replace('words[730]','words[760]').replace('i<730','i<760').replace('crtc_vblank_low_control','crtc_linecompare_high_control').replace('result.cb15_cleanup_mask){','result.cb15_cleanup_mask || result.cl7_cleanup_mask){').replace('result.code==0x80742)','result.code==0x80742 || result.code==0x80744)')
 assert main==expected
 assert (K/'Makefile').read_text()==ns((O/'Makefile').read_text()).replace('CR15 VBLANK LOW','CR07 LINECOMPARE HIGH')
 assert 'pci[9]==0x8001' in main and 'pci[9]==0x8071' not in main
 assert '(o->cr0&0x80000001)!=0x80000001' in probe
 legacy=K.parent/'xcal-transaction704/gpu_legacy.c'
 assert sha(legacy)=='5e686c6e875f9d9bb60a0955bedfb4978911f5a79bf1feaea47080d9d7fe5690'
 assert compact('m = 0x3ff; b = NvGetCrtc(pbRegs, 7) & 0xef; NvSetCrtc(pbRegs, 7, b | ((m >> 4) & 0x10));') in compact(re.sub(r'//[^\n]*','',legacy.read_text()))
 from audit_logic import validate
 m=read(K/'model005.json');assert m['passed'] and len(m['cases'])==974
 for c in m['cases']:validate(c['raw_result'])
 base=m['cases'][0]['raw_result'];assert base[730:]==[62,62,1,62,62,0]+[v for a in values for v in [a]*3]
 mutations=[]
 for i in [0,1,28,30,83,90,97,98,100,101]+list(range(104,760)):
  v=base.copy();v[i]^=1
  try:validate(v)
  except AssertionError:mutations.append(i)
  else:raise AssertionError(('accepted mutation',i))
 for c in m['cases']:
  if c['raw_result'][735]:
   assert c['raw_result'][0]==0x80745 and c['raw_result'][101]==0 and c['ports']==[5]
   v=c['raw_result'].copy();v[101]=1
   try:validate(v)
   except AssertionError:pass
   else:raise AssertionError('unsafe output-enable admitted')
 checks=['build002.json','model005.json','layout-model001.json','clock-model004.json','frontend-model002.json','link-review001.json','layout-link-review001.json','main-link-review001.json','controller-review003.json']
 assert all(read(K/n)['passed'] for n in checks)
 assert read(K/'layout-model001.json')['case_count']==2353
 assert len(read(K/'clock-model004.json')['cases'])==10
 f=read(K/'frontend-model002.json');assert f['case_count']==26 and f['hardware_PCI_literal']==0x8001
 assert not f['cases'][0]['refused'] and all(c['refused'] for c in f['cases'][1:])
 save('schema001.json',dict(words=760,bytes=3040,inherited='CLOSED805 source contract; appended30 words',baseline=62,target=62,restoration='own saved CR07 before CR15 blank recovery',recovery_mask_count=31,same_value_dropped_write_or_undo_indistinguishable=True))
 save('source-review003.json',dict(passed=True,exact_source_only_delta=True,PCI_literal=0x8001,compiled_frontend_cases=26,register_model_cases=974,rejected_schema_mutations=mutations,no_physical_proof=True))
 checks+=['schema001.json','source-review003.json','lineage001.json','qualification-failure001.json']
 r.update(passed=True,checks={n:sha(K/n) for n in checks},model_cases=974,frontend_cases=26,physical_proof=False)
 save('sources001.json',{p.name:sha(p) for p in K.iterdir() if p.suffix in ['.c','.h','.py'] or p.name in ['Makefile','.gitattributes','.gitignore']})
except BaseException as e:r['failure']=repr(e);raise
finally:r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save('review003.json',r)
print('PASS807 source, compiled frontend and complete schema review')
