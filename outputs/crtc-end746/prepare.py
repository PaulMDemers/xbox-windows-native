"""Author distinct746 source from closed744 source only; never reuse runtime."""
from pathlib import Path
import json,hashlib
K=Path(__file__).resolve().parent;O=K.parent/'crtc-start744'
assert not (K/'probe.c').exists()
names=['main.c','layout.c','layout.h','probe.c','probe.h','Makefile','build.py','model004.py','layout_model.py','link_review.py','layout_link_review.py','main_link_review.py','audit_logic.py','prefix_schema.py','physical.py','audit_collection.py']
for n in names:
 s=(O/n).read_text().replace('744','746').replace('crtc_start_control','crtc_end_control')
 (K/('model.py' if n=='model004.py' else n)).write_text(s,newline='\n')
def edit(n,changes):
 p=K/n;s=p.read_text()
 for a,b in changes:assert a in s,(n,a);s=s.replace(a,b)
 p.write_text(s,newline='\n')
edit('probe.h',[('};',' uint32_t c5_target,c5_attempted,c5_after,c4_after;\n};')])
edit('probe.c',[
 ('Distinct CR04 checkpoint. One additional CRTC byte after','Distinct CR05 low-five-bit checkpoint after'),
 ('the preserving prefix and seven horizontal words. No CR05 data write.','the preserving prefix, seven horizontal words, and qualified CR04 write.'),
 (' o->c4_checked=o->c4_restored=o->c5_checked=o->c5_restored=0xffffffff;',' o->c4_checked=o->c4_restored=o->c5_checked=o->c5_restored=0xffffffff;\n o->c5_after=o->c4_after=0xffffffff;'),
 (' o->forward_status=0x746;\nrestore:', ''' /* Original next read/modify/write: preserve CR05 upper three bits. */
 o->c5_target=(o->c5_checked&0xe0)|((((779u-32u+16u)/8u)-1u)&0x1f);
 o->c5_attempted=1;cw(5,(uint8_t)o->c5_target);o->forward_status=0x746d;
 o->c5_after=cr(5);o->c4_after=cr(4);
 if(o->c5_after!=o->c5_target || o->c4_after!=93)goto restore;
 o->forward_status=0x746;
restore:'''),
 (' /* Undo newest access first; never guess a repair for the unwritten CR05. */',' /* Undo only attempted writes, newest first, using own saved full bytes. */\n if(o->c5_attempted)cw(5,(uint8_t)o->c5_before);')])
edit('main.c',[('words[112]','words[116]'),('i<112','i<116'),('result.code==0x746b)','result.code==0x746b || result.code==0x746d)')])
edit('Makefile',[('Kernel\\ CR04','Kernel\\ CR05')])
edit('physical.py',[("'model004.json'","'model001.json'"),('one CR04 byte and own saved-value restoration','CR04 and CR05 bytes with own saved-value restoration'),('CR04 checkpoint after qualified horizontal prefix','CR05 checkpoint after qualified horizontal prefix and CR04')])
edit('audit_collection.py',[('len(v)==112','len(v)==116'),('0x746b]','0x746b,0x746d]')])
edit('model.py',[("out=K/'model004.json'","out=K/'model001.json'")])
(K/'lineage001.json').write_text(json.dumps({'source_only_reuse':True,'parent_source':'outputs/crtc-start744','closed_runtime_reused':False,'files':{n:hashlib.sha256((O/n).read_bytes()).hexdigest() for n in names},'delta':'CR05 upper-three-preserving low-five write after CR04; full-byte/interaction checks; reverse own-value restoration'},indent=2)+'\n',newline='\n')
print('Prepared746 source only')
