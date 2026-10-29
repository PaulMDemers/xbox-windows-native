"""Independent809 source delta, actual compiled admission and full schema review."""
from pathlib import Path
import ast,datetime,hashlib,json,re
K=Path(__file__).resolve().parent;O=K.parent/'crtc-linecompare-high807';P=Path('C:/xwn809/build002')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
def ns(s):
 parts=re.split(r'(0x[0-9a-fA-F]+)',s)
 return ''.join(re.sub(r'^0x807(?=[0-9a-f]{0,2}$)','0x809',p) if i%2 else p.replace('807','809') for i,p in enumerate(parts)).replace('crtc-vblank-low809','crtc-linecompare-bit809')
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
 start=probe.index(' /* CRTC_LINECOMP bit6, pinned704 m=0x3ff; same-value at this baseline. */')
 end=probe.index(' o->forward_status=0x809;\nrestore:',start)
 forward=probe[start:end];body=forward[forward.index('o->forward_status='):]
 regs=[6,7,16,18,21,22,24,37];values=[12,62,233,223,223,140,255,16]
 labels=['cl9_c6','cl9_c7','cl9_c10','cl9_c12','cl9_c15','cl9_c16','cl9_c18','cl9_c25']
 expected='o->forward_status=0x80946;o->cl9_before=cr(9);'
 expected+=''.join(f'o->{n}_before=cr({hex(a)});' for n,a in zip(labels,regs))
 expected+='if(o->cl9_before!=0x40||'+'||'.join(f'o->{n}_before!={hex(v)}' for n,v in zip(labels,values))+')goto restore;'
 expected+='o->cl9_target=(o->cl9_before&0xbfu)|((0x3ffu>>3)&0x40u);o->cl9_attempted=1;cw(9,o->cl9_target);o->cl9_after=cr(9);'
 expected+=''.join(f'o->{n}_after=cr({hex(a)});' for n,a in zip(labels,regs))
 expected+='if(o->cl9_after!=o->cl9_target||'+'||'.join(f'o->{n}_after!=o->{n}_before' for n in labels)+')goto restore;'
 assert compact(body)==compact(expected)
 undo=next(line+'\n' for line in probe.splitlines() if line.startswith(' if(o->cl9_attempted){'))
 expected='if(o->cl9_attempted){cw(9,o->cl9_before);o->cl9_restored=cr(9);'
 expected+=''.join(f'o->{n}_restored=cr({hex(a)});' for n,a in zip(labels,regs))
 expected+='if(o->cl9_restored!=o->cl9_before)o->cl9_cleanup_mask|=1;'
 expected+=''.join(f'if(o->{n}_restored!=o->{n}_before)o->cl9_cleanup_mask|={2<<i};' for i,n in enumerate(labels))+'}'
 assert compact(undo)==compact(expected) and probe.index(undo)<probe.index(' if(o->cl7_attempted){')
 init=next(line+'\n' for line in probe.splitlines() if line.startswith(' o->cl9_after=0xffffffff;'))
 fields=['cl9_before','cl9_target','cl9_attempted','cl9_after','cl9_restored','cl9_cleanup_mask']
 for n in labels:fields.extend([n+'_before',n+'_after',n+'_restored'])
 assert compact(init)==''.join(f'o->{f}=0xffffffff;' for f in fields if f.endswith(('_after','_restored')))
 stripped=probe.replace(forward,'').replace(undo,'').replace(init,'').replace(' && !o->cl9_cleanup_mask','').replace(' if(o->cl9_cleanup_mask)o->code=0x80947;\n','')
 assert stripped==old,'unapproved prefix/source change'
 assert (K/'probe.h').read_text()==ns((O/'probe.h').read_text()).replace('};',' uint32_t '+','.join(fields)+';\n};')
 main=(K/'main.c').read_text();expected=ns((O/'main.c').read_text()).replace('words[760]','words[790]').replace('i<760','i<790').replace('crtc_linecompare_high_control','crtc_linecompare_bit_control').replace('result.cl7_cleanup_mask){','result.cl7_cleanup_mask || result.cl9_cleanup_mask){').replace('result.code==0x80944)','result.code==0x80944 || result.code==0x80946)')
 assert main==expected
 assert (K/'Makefile').read_text()==ns((O/'Makefile').read_text()).replace('CR07 LINECOMPARE HIGH','CR09 LINECOMPARE BIT')
 assert 'pci[9]==0x8001' in main and 'pci[9]==0x8091' not in main
 assert '(o->cr0&0x80000001)!=0x80000001' in probe
 legacy=K.parent/'xcal-transaction704/gpu_legacy.c'
 assert sha(legacy)=='5e686c6e875f9d9bb60a0955bedfb4978911f5a79bf1feaea47080d9d7fe5690'
 assert compact('b = NvGetCrtc(pbRegs, 9) & 0xbf; NvSetCrtc(pbRegs, 9, b | ((m >> 3) & 0x40));') in compact(re.sub(r'//[^\n]*','',legacy.read_text()))
 from audit_logic import validate
 m=read(K/'model006.json');assert m['passed'] and len(m['cases'])==1014
 for c in m['cases']:validate(c['raw_result'])
 base=m['cases'][0]['raw_result'];assert base[760:]==[64,64,1,64,64,0]+[v for a in values for v in [a]*3]
 mutations=[]
 for i in [0,1,28,30,83,90,97,98,100,101]+list(range(104,790)):
  v=base.copy();v[i]^=1
  try:validate(v)
  except AssertionError:mutations.append(i)
  else:raise AssertionError(('accepted mutation',i))
 for c in m['cases']:
  if c['raw_result'][765]:
   assert c['raw_result'][0]==0x80947 and c['raw_result'][101]==0 and c['ports']==[5]
   v=c['raw_result'].copy();v[101]=1
   try:validate(v)
   except AssertionError:pass
   else:raise AssertionError('unsafe output-enable admitted')
 checks=['build002.json','model006.json','layout-model001.json','clock-model005.json','frontend-model002.json','link-review001.json','layout-link-review001.json','main-link-review001.json','controller-review003.json']
 assert all(read(K/n)['passed'] for n in checks)
 assert read(K/'layout-model001.json')['case_count']==2353
 assert len(read(K/'clock-model005.json')['cases'])==10
 f=read(K/'frontend-model002.json');assert f['case_count']==26 and f['hardware_PCI_literal']==0x8001
 assert not f['cases'][0]['refused'] and all(c['refused'] for c in f['cases'][1:])
 save('schema001.json',dict(words=790,bytes=3160,inherited='CLOSED807 source contract; appended30 words',baseline=64,target=64,restoration='own saved CR09 before CR07 linecompare recovery',recovery_mask_count=32,same_value_dropped_write_or_undo_indistinguishable=True))
 save('source-review003.json',dict(passed=True,exact_source_only_delta=True,PCI_literal=0x8001,compiled_frontend_cases=26,register_model_cases=1014,rejected_schema_mutations=mutations,no_physical_proof=True))
 checks+=['schema001.json','source-review003.json','lineage001.json','qualification-failure001.json','qualification-failure002.json']
 r.update(passed=True,checks={n:sha(K/n) for n in checks},model_cases=1014,frontend_cases=26,physical_proof=False)
 save('sources001.json',{p.name:sha(p) for p in K.iterdir() if p.suffix in ['.c','.h','.py'] or p.name in ['Makefile','.gitattributes','.gitignore']})
except BaseException as e:r['failure']=repr(e);raise
finally:r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save('review003.json',r)
print('PASS809 source, compiled frontend and complete schema review')
