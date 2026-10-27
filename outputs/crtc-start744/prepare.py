"""Create distinct744 sources from retained742 source only. No runtime reuse."""
from pathlib import Path
import hashlib,json
K=Path(__file__).resolve().parent;O=K.parent/'horizontal-prefix742'
names=['main.c','layout.c','layout.h','probe.c','probe.h','Makefile','build.py','model.py','layout_model.py','link_review.py','layout_link_review.py','main_link_review.py','physical.py','audit_collection.py','audit_logic.py','prefix_schema.py']
assert not (K/'probe.c').exists()
for n in names:(K/n).write_text((O/n).read_text().replace('742','744').replace('horizontal_prefix_control','crtc_start_control'),newline='\n')
(K/'lineage001.json').write_text(json.dumps({'source_only_reuse':True,'parent_source':str(O.relative_to(K.parents[1])),'closed_runtime_reused':False,'files':{n:hashlib.sha256((O/n).read_bytes()).hexdigest() for n in names},'delta':'One CR04 write after qualified prefix/H7; full-byte CR04/CR05 checks and own-value CR04 recovery before enable'},indent=2)+'\n',newline='\n')
def edit(n,changes):
 s=(K/n).read_text()
 for a,b in changes:
  assert a in s,(n,a);s=s.replace(a,b)
 (K/n).write_text(s,newline='\n')
edit('probe.h',[('};',' uint32_t c4_before,c4_checked,c4_restored,c4_attempted,c4_cleanup_mask,c5_before,c5_checked,c5_restored;\n};')])
edit('probe.c',[
 (' * Distinct kernel horizontal checkpoint. Seven timing writes only, following',' * Distinct CR04 checkpoint. One additional CRTC byte after'),
 (' * the preserving prefix. No vertical, encoder, clock, scanout or CR1b/22/33 write.',' * the preserving prefix and seven horizontal words. No CR05 data write.'),
 (' for(unsigned i=0;i<7;++i)o->h_checked', ' o->c4_checked=o->c4_restored=o->c5_checked=o->c5_restored=0xffffffff;\n for(unsigned i=0;i<7;++i)o->h_checked'),
 (' o->forward_status=0x7442;if(!admitted)', ' o->c4_before=cr(4);o->c5_before=cr(5);\n if(o->c4_before!=0xa7 || o->c5_before!=0x31)admitted=0;\n o->forward_status=0x7442;if(!admitted)'),
 (' o->forward_status=0x744;\nrestore:', ' /* Next original SetGPURegister access only: (779-32)/8 == 93. */\n o->c4_attempted=1;cw(4,93);o->forward_status=0x744b;\n o->c4_checked=cr(4);o->c5_checked=cr(5);\n if(o->c4_checked!=93 || o->c5_checked!=o->c5_before)goto restore;\n o->forward_status=0x744;\nrestore:\n /* Undo newest access first; never guess a repair for the unwritten CR05. */\n if(o->c4_attempted)cw(4,(uint8_t)o->c4_before);\n o->c4_restored=cr(4);o->c5_restored=cr(5);\n if(o->c4_restored!=o->c4_before)o->c4_cleanup_mask|=1;\n if(o->c5_restored!=o->c5_before)o->c4_cleanup_mask|=2;'),
 ('if(!o->h_cleanup_mask){gate(4)', 'if(!o->h_cleanup_mask && !o->c4_cleanup_mask){gate(4)'),
 (' if(o->h_cleanup_mask)o->code=0x744a;', ' if(o->h_cleanup_mask)o->code=0x744a;\n if(o->c4_cleanup_mask)o->code=0x744c;')])
edit('main.c',[('words[104]','words[112]'),('i<104','i<112'),('if(result.h_cleanup_mask)','if(result.h_cleanup_mask || result.c4_cleanup_mask)'),('result.code==0x7449)','result.code==0x7449 || result.code==0x744b)')])
edit('Makefile',[('Kernel\\ Horizontal','Kernel\\ CR04')])
edit('physical.py',[('Seven','Seven'),('seven horizontal timing writes and own saved-value restoration','seven horizontal timing writes then one CR04 byte and own saved-value restoration'),('horizontal-only timing checkpoint','CR04 checkpoint after qualified horizontal prefix')])
edit('audit_collection.py',[('len(v)==104','len(v)==112'),('0x7449]','0x7449,0x744b]')])
print('Created744 source kit; no build, stage or launch')
