"""Create new735 from authored734 source, with bounded register-only CPU work."""
from pathlib import Path
import hashlib,json,sys
K=Path(__file__).resolve().parent;W=K.parents[1];old=K.parent/'cr1b-read734';P=Path('C:/xwn735')
assert not P.exists();sys.path.insert(0,str(W/'tools'));from build_space import require_space
space=require_space(P,20.15);P.mkdir()
names=['main.c','layout.c','layout.h','probe.c','probe.h','Makefile','build.py','model.py','layout_model.py','link_review.py','layout_link_review.py','main_link_review.py','physical.py','audit_logic.py','audit_collection.py']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for n in names:
 assert not (K/n).exists();(K/n).write_text((old/n).read_text().replace('734','735').replace('cr1b_read_control','cr1b_work_control'),newline='\n')
(K/'.gitattributes').write_text('* -text\n')
p=K/'probe.h';p.write_text(p.read_text().replace('};',' uint32_t cpu_iterations,cpu_counter_end,cpu_checksum;\n};'))
p=K/'probe.c';s=p.read_text()
s=s.replace(' for(unsigned n=0;n<16;++n){o->direct[n]=R8(0x6013d5);o->direct_count=n+1;}', ''' o->direct[0]=R8(0x6013d5);o->direct_count=1;
 /* No register/port/memory access inside this fixed register-only loop.
  * It is intervening work, not a calibrated elapsed-time measurement. */
 {uint32_t count=4093,sum=0x13579bdf;
  __asm__ volatile("1: roll $1,%0; xorl $0x9e3779b9,%0; decl %1; jnz 1b"
                   :"+r"(sum),"+r"(count)::"memory","cc");
  o->cpu_iterations=4093;o->cpu_counter_end=count;o->cpu_checksum=sum;
 }
 for(unsigned n=1;n<16;++n){o->direct[n]=R8(0x6013d5);o->direct_count=n+1;}''')
p.write_text(s)
p=K/'main.c';p.write_text(p.read_text().replace('words[112]','words[115]').replace('i<112','i<115').replace('CR1b read blocks before prefix cleanup735','CR1b read blocks with bounded CPU work735'))
p=K/'audit_logic.py';s=p.read_text().replace('len(v)==112','len(v)==115')
s=s.replace(' if cr_attempt==4:', ''' checksum=0x13579bdf
 for _ in range(4093):checksum=(((checksum<<1)|(checksum>>31))&0xffffffff)^0x9e3779b9
 if cr_attempt==4:
  assert v[112:115]==[4093,0,checksum]''')
s=s.replace('  assert v[76:78]==[0,0]', '  assert v[112:115]==[0,0,0]\n  assert v[76:78]==[0,0]')
s=s.replace("'CPU':v[11:14]", "'cpu_work':v[112:115],'CPU':v[11:14]");p.write_text(s)
p=K/'model.py';s=p.read_text().replace('0x2011c0','0x2011cc').replace('0x5e40','0x5e34').replace("'<112I'","'<115I'").replace('0x201000,448','0x201000,460').replace('count=15000','count=40000').replace('time.monotonic()+90','time.monotonic()+150')
s=s.replace("elif sample_policy=='after-direct' and n>=16:cr[idx]=0x85", "elif sample_policy=='after-direct' and n>=16:cr[idx]=0x85\n    elif sample_policy=='read-count-eight' and n>=8:cr[idx]=0x85")
s=s.replace("    n=state['sample_reads'];assert n<32", """    n=state['sample_reads'];assert n<32
    if n==0:assert word(112)==0
    else:
     checksum=0x13579bdf
     for _ in range(4093):checksum=(((checksum<<1)|(checksum>>31))&0xffffffff)^0x9e3779b9
     assert [word(112),word(113),word(114)]==[4093,0,checksum]""")
s=s.replace("elif sample_policy=='after-direct':indexed=[0x85]*16", "elif sample_policy=='after-direct':indexed=[0x85]*16\n   elif sample_policy=='read-count-eight':direct=[5]*8+[0x85]*8;indexed=[0x85]*16")
s=s.replace("['eightyfive','after-first','after-direct','unexpected']", "['eightyfive','after-first','after-direct','unexpected','read-count-eight']")
p.write_text(s)
p=K/'physical.py';s=p.read_text().replace('32 before-cleanup CR1b samples','32 before-cleanup CR1b samples with4093 register-only iterations after first read').replace('32 CR1b reads before cleanup','32 CR1b reads with4093 CPU-only iterations before cleanup');p.write_text(s)
p=K/'audit_collection.py';s=p.read_text().replace('len(v)==112','len(v)==115')
s=s.replace(" assert observation['top_bar']==expected and observation['automatic_return_observed'] and not observation['manual_reset']", " assert observation['mode']=='unattended_authorized' and observation['manual_reset_reported']==False\n poll=read(K/'dashboard001.json');assert poll['reachable']\n assert observation['visual_result']=='not_observed'")
s=s.replace('automatic_dashboard_return=True,','automatic_dashboard_return_inferred=True,visual_result_observed=False,expected_top_bar=expected,');p.write_text(s)
(K/'lineage001.json').write_text(json.dumps({'source_only':True,'closed_runtime_reused':False,'space':space,'sources':{n:sha(old/n) for n in names},'scope':'734 exact data writes/cleanup/predicate; inserted CPU-only work after first direct read. Unattended file-based collection authorized by user.'},indent=2)+'\n')
print('735 authored sources prepared; no build/stage/launch')
