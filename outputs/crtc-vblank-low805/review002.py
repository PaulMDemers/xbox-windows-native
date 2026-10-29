"""Independent805 source delta, compiled admission and complete schema review."""
from pathlib import Path
import ast,datetime,hashlib,json,re
K=Path(__file__).resolve().parent;O=K.parent/'crtc-vblank-overflow803';P=Path('C:/xwn805/build002')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
def ns(s):
 parts=re.split(r'(0x[0-9a-fA-F]+)',s)
 return ''.join(re.sub(r'^0x803(?=[0-9a-f]{0,2}$)','0x805',p) if i%2 else p.replace('803','805') for i,p in enumerate(parts)).replace('crtc-vblank-overflow805','crtc-vblank-low805')
def save(n,r):
 with (K/n).open('x') as f:json.dump(r,f,indent=2);f.write('\n')
compact=lambda s:re.sub(r'\s+','',s)
r=dict(passed=False,reviewer_sha256=sha(Path(__file__)));assert not (K/'review002.json').exists()
try:
 assert read(O/'closed001.json')['closed'] and read(O/'closed001.json')['passed']
 for p in K.glob('*.py'):ast.parse(p.read_text())
 for n in ['probe.c','probe.h','main.c','layout.c','layout.h','Makefile']:assert sha(K/n)==sha(P/n),n
 for n in ['layout.c','layout.h','prefix_schema.py']:assert (K/n).read_text()==ns((O/n).read_text()),n
 probe=(K/'probe.c').read_text();old=ns((O/'probe.c').read_text())
 # The only new forward stores are one saved-value CR15 transaction. Inspect its
 # instruction sequence independently, then remove it and compare the full prefix.
 start=probe.index(' /* CRTC_VBLANKSTART low byte, pinned704 yres480 minus1. */')
 end=probe.index(' o->forward_status=0x805;\nrestore:',start)
 forward=probe[start:end];body=forward[forward.index('o->forward_status='):]
 regs=[6,7,9,16,18,22,24,37];values=[12,62,64,233,223,140,255,16]
 labels=['cb15_c'+str(i) for i in regs]
 expected='o->forward_status=0x80542;o->cb15_before=cr(0x15);'
 expected+=''.join(f'o->{n}_before=cr({hex(a)});' for n,a in zip(labels,regs))
 expected+='if(o->cb15_before!=0xcf||'+'||'.join(f'o->{n}_before!={hex(v)}' for n,v in zip(labels,values))+')goto restore;'
 expected+='o->cb15_target=(480u-1u)&0xffu;o->cb15_attempted=1;cw(0x15,o->cb15_target);o->cb15_after=cr(0x15);'
 expected+=''.join(f'o->{n}_after=cr({hex(a)});' for n,a in zip(labels,regs))
 expected+='if(o->cb15_after!=o->cb15_target||'+'||'.join(f'o->{n}_after!=o->{n}_before' for n in labels)+')goto restore;'
 assert compact(body)==compact(expected)
 undo=next(line+'\n' for line in probe.splitlines() if line.startswith(' if(o->cb15_attempted){'))
 expected='if(o->cb15_attempted){cw(0x15,o->cb15_before);o->cb15_restored=cr(0x15);'
 expected+=''.join(f'o->{n}_restored=cr({hex(a)});' for n,a in zip(labels,regs))
 expected+='if(o->cb15_restored!=o->cb15_before)o->cb15_cleanup_mask|=1;'
 expected+=''.join(f'if(o->{n}_restored!=o->{n}_before)o->cb15_cleanup_mask|={2<<i};' for i,n in enumerate(labels))+'}'
 assert compact(undo)==compact(expected)
 assert probe.index(undo)<probe.index(' if(o->cb7_attempted){')
 init=next(line+'\n' for line in probe.splitlines() if line.startswith(' o->cb15_after=0xffffffff;'))
 fields=['cb15_before','cb15_target','cb15_attempted','cb15_after','cb15_restored','cb15_cleanup_mask']
 for n in labels:fields.extend([n+'_before',n+'_after',n+'_restored'])
 assert compact(init)==''.join(f'o->{f}=0xffffffff;' for f in fields if f.endswith(('_after','_restored')))
 stripped=probe.replace(forward,'').replace(undo,'').replace(init,'').replace(' && !o->cb15_cleanup_mask','').replace(' if(o->cb15_cleanup_mask)o->code=0x80543;\n','')
 assert stripped==old,'unapproved prefix/source change'
 assert (K/'probe.h').read_text()==ns((O/'probe.h').read_text()).replace('};',' uint32_t '+','.join(fields)+';\n};')
 main=(K/'main.c').read_text();expected=ns((O/'main.c').read_text()).replace('words[700]','words[730]').replace('i<700','i<730').replace('crtc_vblank_overflow_control','crtc_vblank_low_control').replace('result.cb7_cleanup_mask){','result.cb7_cleanup_mask || result.cb15_cleanup_mask){').replace('result.code==0x80540)','result.code==0x80540 || result.code==0x80542)')
 assert main==expected
 assert (K/'Makefile').read_text()==ns((O/'Makefile').read_text()).replace('CR07 VBLANK OVERFLOW','CR15 VBLANK LOW')
 assert 'pci[9]==0x8001' in main and 'pci[9]==0x8051' not in main
 assert '(o->cr0&0x80000001)!=0x80000001' in probe
 legacy=K.parent/'xcal-transaction704/gpu_legacy.c'
 assert sha(legacy)=='5e686c6e875f9d9bb60a0955bedfb4978911f5a79bf1feaea47080d9d7fe5690'
 assert compact('NvSetCrtc(pbRegs, 0x15, ((gpu->yres - 1) & 0xff));') in compact(legacy.read_text())
 from audit_logic import validate
 m=read(K/'model005.json');assert m['passed'] and len(m['cases'])==934
 for c in m['cases']:validate(c['raw_result'])
 base=m['cases'][0]['raw_result'];assert base[700:]==[207,223,1,223,207,0]+[v for a in values for v in [a]*3]
 mutations=[]
 for i in [0,1,28,30,83,90,97,98,100,101]+list(range(104,730)):
  v=base.copy();v[i]^=1
  try:validate(v)
  except AssertionError:mutations.append(i)
  else:raise AssertionError(('accepted mutation',i))
 for c in m['cases']:
  if c['raw_result'][705]:
   assert c['raw_result'][0]==0x80543 and c['raw_result'][101]==0 and c['ports']==[5]
   v=c['raw_result'].copy();v[101]=1
   try:validate(v)
   except AssertionError:pass
   else:raise AssertionError('unsafe output-enable admitted')
 checks=['build002.json','model005.json','layout-model001.json','clock-model004.json','frontend-model002.json','link-review001.json','layout-link-review001.json','main-link-review001.json','controller-review002.json']
 assert all(read(K/n)['passed'] for n in checks)
 assert read(K/'layout-model001.json')['case_count']==2353
 assert len(read(K/'clock-model004.json')['cases'])==10
 f=read(K/'frontend-model002.json');assert f['case_count']==26 and f['hardware_PCI_literal']==0x8001
 assert not f['cases'][0]['refused'] and all(c['refused'] for c in f['cases'][1:])
 save('schema001.json',dict(words=730,bytes=2920,inherited='CLOSED803 source contract; appended30 words',baseline=207,target=223,restoration='own saved CR15 before CR07 blank recovery',recovery_mask_count=30))
 save('source-review002.json',dict(passed=True,exact_source_only_delta=True,PCI_literal=0x8001,compiled_frontend_cases=26,register_model_cases=934,rejected_schema_mutations=mutations,no_physical_proof=True))
 checks+=['schema001.json','source-review002.json','lineage001.json','qualification-failure001.json','qualification-failure002.json','qualification-failure003.json']
 r.update(passed=True,checks={n:sha(K/n) for n in checks},model_cases=934,frontend_cases=26,physical_proof=False)
 save('sources001.json',{p.name:sha(p) for p in K.iterdir() if p.suffix in ['.c','.h','.py'] or p.name in ['Makefile','.gitattributes','.gitignore']})
except BaseException as e:r['failure']=repr(e);raise
finally:r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save('review002.json',r)
print('PASS805 source, compiled frontend and complete schema review')
