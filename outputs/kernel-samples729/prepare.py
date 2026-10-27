"""Fresh729 source from closed728 authored files only; no runtime reuse."""
from pathlib import Path
import json,hashlib,datetime
K=Path(__file__).resolve().parent;S=K.parent/'kernel-interaction728';P=Path('C:/xwn729')
assert not P.exists();P.mkdir()
files=['main.c','probe.c','probe.h','layout.c','layout.h','Makefile','build.py','model.py','layout_model.py','link_review.py','layout_link_review.py','main_link_review.py','physical.py','audit_collection.py']
lineage={}
for name in files:
 b=(S/name).read_bytes();lineage[name]=hashlib.sha256(b).hexdigest()
 (K/name).write_text(b.decode().replace('\r\n','\n').replace('728','729'),newline='\n')
f=K/'probe.h';t=f.read_text().replace('\n};','\n uint32_t blank630[32],blank1b[32],blank_count,blank_changes,blank_min,blank_max;\n uint32_t gate630,gate1b,gate_seq;\n};');f.write_text(t,newline='\n')
f=K/'probe.c';t=f.read_text();t=t.replace(' uint32_t flags,restored;',' uint32_t flags,restored;')
t=t.replace(' for(unsigned i=0;i<6;++i)', ' for(unsigned i=0;i<32;++i)o->blank630[i]=o->blank1b[i]=0xffffffff;\n o->gate630=o->gate1b=o->gate_seq=0xffffffff;\n for(unsigned i=0;i<6;++i)',1)
t=t.replace('restore_output:\n gate(4);sw((uint8_t)o->seq_before);', ''' /* Observe bounded pairs before any output-restoration write. Extra reads
  * alter timing; a first change near a write is not proof of causality. */
 o->blank_min=o->blank_max=o->cr1b[3];
 {uint32_t last=o->cr1b[3];
  for(unsigned n=0;n<32;++n){
   uint8_t index=R8(0x6013d4);
   o->blank630[n]=R32(0x680630);o->blank1b[n]=cr(0x1b);R8(0x6013d4)=index;
   o->blank_count++;
   if(o->blank1b[n]!=last)o->blank_changes++;
   last=o->blank1b[n];
   if(last<o->blank_min)o->blank_min=last;
   if(last>o->blank_max)o->blank_max=last;
  }
 }
restore_output:
 gate(4);
 {uint8_t index=R8(0x6013d4);
  o->gate630=R32(0x680630);o->gate1b=cr(0x1b);R8(0x6013d4)=index;
 }
 o->gate_seq=sr();
 sw((uint8_t)o->seq_before);''')
assert 'blank_count++' in t;f.write_text(t,newline='\n')
f=K/'main.c';t=f.read_text().replace('minimal630/CR1b interaction729','blank/gate/sequencer sampling729').replace('kernel_interaction_words','kernel_sample_words').replace('words[54]','words[125]').replace('i<54','i<125');f.write_text(t,newline='\n')
f=K/'physical.py';t=f.read_text().replace('minimal630/CR1b interaction','bounded blank/gate/sequencer sampling').replace('minimal6302/oneCR1b05/saved6303; preserve full-byte final checks','minimal6302/oneCR1b05/saved6303 with32blank pairs and gate-beforeSEQ sample; full-byte final checks');f.write_text(t,newline='\n')
(K/'.gitattributes').write_text('* -text\n',newline='\n')
(K/'lineage001.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'parent':'kernel-interaction728 CLOSED; source reuse only','sources':lineage,'new_data_writes':False,'additional_samples':'32 full pairs while blank; full pair andSEQ1 aftergate4 beforeSEQ1 restore','native_transition':False,'closed_runtime_reused':False},indent=2)+'\n',newline='\n')
(P/'connection.json').write_bytes(Path('C:/xwn728/connection.json').read_bytes())
print('Prepared729 authored source; no hardware access')
