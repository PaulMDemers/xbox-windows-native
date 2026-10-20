"""Prepare a fresh uninstrumented saved-scene control; scoped namespace edits only."""
import hashlib,json,re
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];S=K.parent/'rct602'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (K/'source001.json').exists()
sources={}
def copy(name,source=S,edits=()):
 p=source/name;text=p.read_text(encoding='utf-8')
 for a,b in [('xwn602','xwn603'),('rct602','rct603'),('run602','run603'),('RUN602','RUN603'),('verify602','verify603'),('VERIFY602','VERIFY603')]+list(edits):text=text.replace(a,b)
 (K/name).write_text(text,encoding='utf-8',newline='\n');sources[name]=dict(source=str(p),sha256=sha(p))
for n in ['verify.c','asset_header_check001.py','input_transport001.py','login001.py','cold002.py','binary_review001.py','welcome.h','game_capture.h','title_signature.h']:
 copy(n)
copy('vm.py',edits=[('choices=[602]','choices=[603]')])
copy('actions002.py',edits=[("'602'","'603'")])
copy('prepare001.py',edits=[("print('Prepared fresh599 phase1; single instrumented discovery boot; no performance control')","print('Prepared fresh603 saved-scene fixture; uninstrumented game')")])
copy('build001.py',edits=[(",('trace.c','trace602.exe')",'')])
copy('runner.c',K.parent/'rct593',edits=[('xwn593','xwn603'),('number("schema",586)','number("schema",603)')])
p=K/'runner.c';s=p.read_text();old='number("initial_height",initialheight);';assert s.count(old)==1
s=s.replace(old,old+'\n if(initialwidth!=1024||initialheight!=768){number("display_preflight_failed",1);goto end;}number("display_preflight_passed",1);');p.write_text(s,encoding='utf-8',newline='\n')
copy('input.h');p=K/'input.h';s=p.read_text();s=s.replace('static BOOL runinputs(void){','#include "load_dialog.h"\nstatic BOOL runinputs(void){')
old=' return capture("park-api-observation");';assert old in s
s=s.replace(old,''' if(!capture("park-before-move")||!point(5,5))return FALSE;
 {INPUT i;BOOL down,up;keyevent(&i,VK_RIGHT,FALSE);down=SendInput(1,&i,sizeof(i))==1;Sleep(2000);
 keyevent(&i,VK_RIGHT,TRUE);up=SendInput(1,&i,sizeof(i))==1;number("camera_right_submitted",down&&up);if(!down||!up)return FALSE;}
 Sleep(1000);
 if(!capture("camera-moved")||!click(44,14)||!capture("load-menu")||!click(76,40))return FALSE;
 if(!load_owned_park())return FALSE;
 if(!point(5,5)||!capture("park-loaded"))return FALSE;
 Sleep(10000);
 return capture("park-loaded-stable");''');p.write_text(s,encoding='utf-8',newline='\n')
save=Path('C:/xwn593/pc001/cold1-002/files/xwn593-kit/game/Saved Games/XWN593.SV4')
ref=Path('C:/xwn593/pc001/collection001/06-park-after-save.bmp')
assert save.stat().st_size==290244 and sha(save)=='ca9a26c940a6dfc8dc5ba53cf8717eb4eb7b247140aa636a0afd29b9bbf5947e'
assert sha(ref)=='8178f585ddb10d28e2011f7dc446c40509143b80aae96cdcaf38f37afdea0e1d'
a=json.loads((S/'asset-integrity001.json').read_text());name='game/Saved Games/XWN593.SV4'
a[name]=dict(bytes=save.stat().st_size,sha256=sha(save),sha1=hashlib.sha1(save.read_bytes()).hexdigest())
(K/'asset-integrity001.json').write_text(json.dumps(a,indent=2)+'\n')
h=['/* MIT. Hash metadata only; retail files plus exact retained PC593 save. */','static const struct {const char *path;DWORD size;BYTE sha1[20];} assets[]={']
for name,v in sorted(a.items()):
 escaped=name.replace('/','\\\\');h.append('{"'+escaped+'",'+str(v['bytes'])+',{'+','.join(str(b) for b in bytes.fromhex(v['sha1']))+'}},')
h+=['};'];(K/'assets.h').write_text('\n'.join(h)+'\n')
(K/'.gitattributes').write_text('* -text whitespace=cr-at-eol\n')
(K/'edition.json').write_text('{"fixture":"/mnt/c/xwn603/pc001"}\n')
(K/'source001.json').write_text(json.dumps(dict(passed=True,sources=sources,save=dict(path=str(save),sha256=sha(save),sha1=a[name]['sha1'] if name=='game/Saved Games/XWN593.SV4' else hashlib.sha1(save.read_bytes()).hexdigest(),bytes=save.stat().st_size),reference=dict(path=str(ref),sha256=sha(ref)),physical_access=False,game_instrumentation=False),indent=2)+'\n')
print('603 prepared sources; exact PC593 save,503 assets, no debugger')
