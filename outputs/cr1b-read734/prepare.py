"""Prepare new734 from authored733 source only, never reuse a closed runtime."""
from pathlib import Path
import hashlib,json,sys
K=Path(__file__).resolve().parent;W=K.parents[1];old=K.parent/'batch-prefix733'
P=Path('C:/xwn734');assert not P.exists()
sys.path.insert(0,str(W/'tools'));from build_space import require_space
space=require_space(P,20.15);P.mkdir()
names=['main.c','layout.c','layout.h','probe.c','probe.h','Makefile','build.py','model.py','layout_model.py','link_review.py','layout_link_review.py','main_link_review.py','physical.py','audit_logic.py','audit_collection.py']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name in names:
 assert not (K/name).exists()
 text=(old/name).read_text().replace('733','734').replace('batch_prefix_control','cr1b_read_control')
 (K/name).write_text(text,newline='\n')
(K/'.gitattributes').write_text('* -text\n')
p=K/'probe.h';s=p.read_text().replace('};',' uint32_t direct_count,indexed_count,after_direct630,after_indexed630;\n uint32_t direct[16],indexed[16];\n};');p.write_text(s)
p=K/'probe.c';s=p.read_text().replace(' * Batch all writes, then check in original order. No interleaved readback.',' * Batch all writes, sample CR1b before cleanup, then retain original checks.\n * Two ordered read blocks are observations, not a timing or selector-cause proof.')
s=s.replace(' uint32_t flags,restored;*o=', ' uint32_t flags,restored;*o=')
s=s.replace(' for(unsigned i=0;i<11;++i)o->mmio_checked', ' o->after_direct630=o->after_indexed630=0xffffffff;\n for(unsigned i=0;i<16;++i)o->direct[i]=o->indexed[i]=0xffffffff;\n for(unsigned i=0;i<11;++i)o->mmio_checked',1)
s=s.replace(' o->forward_status=0x7348;',''' /* The last write selected CR1b. First block has no selector write or other
  * MMIO read before/between its16 direct byte reads. Bounded RAM records only.
  * The second block reselects CR1b for each read. Their order is a confounder.
  * No data write, gate/SEQ write or630 restoration occurs in this interval. */
 for(unsigned n=0;n<16;++n){o->direct[n]=R8(0x6013d5);o->direct_count=n+1;}
 o->after_direct630=R32(0x680630);
 for(unsigned n=0;n<16;++n){o->indexed[n]=cr(0x1b);o->indexed_count=n+1;}
 o->after_indexed630=R32(0x680630);
 o->forward_status=0x7348;''',1);p.write_text(s)
p=K/'main.c';s=p.read_text().replace('words[76]','words[112]').replace('i<76','i<112')
s=s.replace('/* SPDX-License-Identifier: MIT','/* SPDX-License-Identifier: MIT',1)
p.write_text(s)
p=K/'audit_collection.py';p.write_text(p.read_text().replace('len(v)==76','len(v)==112'))
p=K/'audit_logic.py';s=p.read_text().replace('len(v)==76','len(v)==112')
s=s.replace(' return {', ''' if cr_attempt==4:
  assert v[76:78]==[16,16] and all(n<=255 for n in v[80:112])
 else:
  assert v[76:78]==[0,0] and v[78:112]==[0xffffffff]*34
 return {''')
s=s.replace("'CPU':v[11:14]", "'sample_counts':v[76:78],'sample630':v[78:80],'direct':v[80:96],'indexed':v[96:112],'CPU':v[11:14]")
p.write_text(s)
p=K/'physical.py';s=p.read_text().replace('kernel-context 11 MMIO and four CRTC setup-prefix writes, deferred ordered readback','kernel-context qualified prefix writes,32 CR1b reads before cleanup, deferred ordered readback').replace('batched setup-prefix writes and first-mismatch capture','batched setup-prefix writes,32 before-cleanup CR1b samples and first-mismatch capture');p.write_text(s)
p=K/'model.py';s=p.read_text().replace('baseline=""):', 'baseline="",sample_policy="five"):')
s=s.replace("'unlock':False}","'unlock':False,'sample_reads':0,'sample_selector_writes':0}")
s=s.replace("if kind==u.UC_MEM_WRITE:sels[off]=value;return", """if kind==u.UC_MEM_WRITE:
    if off==0x6013d4 and word(3)==4 and word(1)==0x7344 and value==0x1b:
     state['sample_selector_writes']+=1
    sels[off]=value;return""")
s=s.replace('   val=cr[idx]\n', '''   if idx==0x1b and word(3)==4 and word(1)==0x7344 and not state['recovering']:
    n=state['sample_reads'];assert n<32
    assert mm[0x680630]==2
    assert state['sample_selector_writes']==(0 if n<16 else n-15)
    if sample_policy=='eightyfive':cr[idx]=0x85
    elif sample_policy=='after-first' and n>=1:cr[idx]=0x85
    elif sample_policy=='after-direct' and n>=16:cr[idx]=0x85
    elif sample_policy=='unexpected':cr[idx]=4
    state['sample_reads']+=1
   val=cr[idx]
''',1)
s=s.replace('0x201130','0x2011c0').replace('0x5ed0','0x5e40').replace("'<76I'","'<112I'").replace('0x201000,304','0x201000,448')
s=s.replace("else 0x7348 if fault.startswith('check-') else 0x734", "else 0x7348 if fault.startswith('check-') or sample_policy!='five' else 0x734")
s=s.replace("fail=int(fault.split('-')[1]) if fault.startswith('check-') else None", "fail=int(fault.split('-')[1]) if fault.startswith('check-') else 14 if sample_policy!='five' else None")
s=s.replace("   for n,value in enumerate(checked):", """   actual=(4 if sample_policy=='unexpected' else 0x85) if sample_policy!='five' else expected[fail]^1 if fail is not None else 0
   assert v[76:80]==[16,16,2,2] and state['sample_reads']==32 and state['sample_selector_writes']==16
   direct=[5]*16;indexed=[5]*16
   if sample_policy=='eightyfive':direct=indexed=[0x85]*16
   elif sample_policy=='after-first':direct=[5]+[0x85]*15;indexed=[0x85]*16
   elif sample_policy=='after-direct':indexed=[0x85]*16
   elif sample_policy=='unexpected':direct=indexed=[4]*16
   assert v[80:112]==direct+indexed
   for n,value in enumerate(checked):""")
s=s.replace("expected[n]^(1 if n==fail else 0)","actual if n==fail else expected[n]")
s=s.replace('expected[fail]^1]','actual]')
s=s.replace("else:assert v[2:4]==[0,0] and v[7]==0", "else:assert v[2:4]==[0,0] and v[7]==0 and v[76:78]==[0,0] and v[78:112]==[0xffffffff]*34")
s=s.replace(" run('baseline-deferred-read-success')", " run('baseline-deferred-read-success')\n for policy in ['eightyfive','after-first','after-direct','unexpected']:run('hypothetical-'+policy,sample_policy=policy)")
p.write_text(s)
(K/'lineage001.json').write_text(json.dumps({'source_only':True,'closed_runtime_reused':False,'source_files':{n:sha(old/n) for n in names},'space':space,'scope':'Authored733 sources, appended bounded observations only; qualified data-write/recovery sequence and full-byte deferred predicate unchanged.'},indent=2)+'\n')
print('Prepared734 source only; no build, stage or launch')
