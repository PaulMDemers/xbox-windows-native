from pathlib import Path
import json,hashlib,datetime
k=Path(__file__).resolve().parent
p=Path('C:/xwn728');assert not p.exists();p.mkdir()
native=k.parent/'native-interaction727';source=k.parent/'kernel-prefix723'
lineage={}
for name in ['main.c','layout.c','layout.h','Makefile','build.py','layout_model.py','link_review.py','layout_link_review.py','physical.py']:
 b=(source/name).read_bytes();lineage[str(source/name)]=hashlib.sha256(b).hexdigest();(k/name).write_text(b.decode().replace('723','728'),newline='\n')
for name in ['probe.c','probe.h']:
 b=(native/name).read_bytes();lineage[str(native/name)]=hashlib.sha256(b).hexdigest();(k/name).write_text(b.decode().replace('727','728'),newline='\n')
f=k/'probe.c';t=f.read_text();old='(o->cr0&0xe0000001)!=0x40000001 || o->cr3!=0 || (flags&0x200)';assert old in t;t=t.replace(old,'(o->cr0&0x80000001)!=0x80000001');f.write_text(t,newline='\n')
f=k/'main.c';t=f.read_text().replace('Kernel-context CR1b saved-value control728','Kernel-context minimal630/CR1b interaction728').replace('kernel_setup_prefix_words','kernel_interaction_words').replace('words[66]','words[54]').replace('i<66','i<54').replace('result.code==0x7288?0xff8000','(result.code==0x7288 || result.code==0x7285)?0xff8000');f.write_text(t,newline='\n')
f=k/'physical.py';t=f.read_text().replace('common-setup prefix before CR22','minimal630/CR1b interaction').replace('common-setup prefix; stop before CR22; retain05 if CR1b attempted','minimal6302/oneCR1b05/saved6303; preserve full-byte final checks');f.write_text(t,newline='\n')
(k/'.gitattributes').write_text('* -text\n')
(k/'lineage001.json').write_text(json.dumps({'source_reuse_only':True,'closed_runtimes_reused':False,'parent_hashes':lineage,'probe_changes':['namespace727->728','kernel CPU admission only; register body and result layout unchanged'],'main_changes':['54 raw words after flags restored','orange includes final baseline mismatch7285'],'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()},indent=2)+'\n')
(p/'connection.json').write_bytes(Path('C:/xwn727/connection.json').read_bytes())
print('Created fresh728 source/private paths; no hardware access')
