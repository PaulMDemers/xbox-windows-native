"""Compose qualified retail handoff, saved-scene input and phase/header observer."""
import hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'work/python-packages'));from PIL import Image
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (K/'source001.json').exists()
sources={}
def copy(n,old,src=None):
 p=K.parent/f'rct{old}'/(src or n);s=p.read_text(encoding='utf-8')
 for a,b in [(f'xwn{old}','xwn606'),(f'XWN{old}','XWN606'),(f'rct{old}','rct606'),(f'run{old}','run606'),(f'RUN{old}','RUN606'),(f'verify{old}','verify606'),(f'VERIFY{old}','VERIFY606'),(f'trace{old}','trace606'),(f'choices=[{old}]','choices=[606]'),(f"'{old}'","'606'")]:s=s.replace(a,b)
 (K/n).write_text(s,encoding='utf-8',newline='\n');sources[n]=dict(source=str(p),sha256=sha(p))
for n in ['verify.c','asset_header_check001.py','assets.h','asset-integrity001.json','input_transport001.py','login001.py','cold002.py','binary_review001.py','welcome.h','game_capture.h','title_signature.h','vm.py','actions002.py','prepare001.py','media001.py','media_review001.py','scene_compare.py','scene_tests001.py']:
 copy(n,603)
copy('runner.c',602)
copy('input.h',603,'input002.h');copy('load_dialog002.h',603)
for n in ['trace.c','phase.h','dib_header.h','calls.h','dib_oracle.py','event_timestamps001.py']:
 copy(n,605)
copy('trace_oracle.py',605,'trace_oracle002.py')
copy('target_iat.h',602)
copy('build001.py',603,'build002.py')
# Retail observer uses the exact605 helper prefix and602's launch/PID handoff.
p=K/'trace.c';s=p.read_text()
s=s.replace('char cmd[]="subject605 traced";','char cmd[]="\\"C:\\\\xwn606-kit\\\\game\\\\RCT.EXE\\"";HANDLE pidfile;DWORD done;')
s=s.replace('C:\\\\xwn606-kit\\\\subject.exe','C:\\\\xwn606-kit\\\\game\\\\RCT.EXE')
s=s.replace('0,"C:\\\\xwn606-kit",&si,&pi)','0,"C:\\\\xwn606-kit\\\\game",&si,&pi)')
needle='process=pi.hProcess;CloseHandle(pi.hThread);started=GetTickCount();'
handoff=(K.parent/'rct602/trace.c').read_text().split(needle,1)[1].split('    while(!exited)',1)[0].replace('xwn602','xwn606')
s=s.replace(needle,needle+handoff.rstrip()).replace('GetTickCount()-started>60000','GetTickCount()-started>360000')
p.write_text(s,encoding='utf-8',newline='\n')
# Sample pixels are hashed before freeing the private capture DIB.
p=K/'input.h';s=p.read_text();s=s.replace('static BOOL gamecapture(const char* tag);','#include "park_phase.h"\nstatic BOOL gamecapture(const char* tag);')
needle='ok=bytes(file,&header,sizeof(header))&&bytes(file,&info.bmiHeader,sizeof(BITMAPINFOHEADER))&&bytes(file,bits,info.bmiHeader.biSizeImage);'
assert s.count(needle)==1
s=s.replace(needle,needle+'\n if(ok&&(lstrcmpA(tag,"park-loaded")==0||lstrcmpA(tag,"park-loaded-stable")==0)){ok=parkhash606((const BYTE*)bits);number("park_reference_match",ok);if(ok)park_verified=TRUE;}')
s=s.replace('Sleep(10000);\n return capture("park-loaded-stable");','if(!parkphase606())return FALSE;\n Sleep(10000);\n return capture("park-loaded-stable");')
p.write_text(s,encoding='utf-8',newline='\n')
# Build all three tools. Immutable output and receipt names are new606 build001.
p=K/'build001.py';s=p.read_text().replace('build002','build001').replace("('runner002.c','run606.exe')","('runner.c','run606.exe')").replace("('verify.c','verify606.exe')]","('verify.c','verify606.exe'),('trace.c','trace606.exe')]")
p.write_text(s,encoding='utf-8',newline='\n')
for name in ['binary_review001.py','media001.py']:
 p=K/name;s=p.read_text().replace('build002.json','build001.json');p.write_text(s,encoding='utf-8',newline='\n')
p=K/'media001.py';s=p.read_text()
needle="'copy D:\\\\VERIFY606.EXE C:\\\\xwn606-kit\\\\VERIFY606.EXE'"
assert s.count(needle)==1
s=s.replace(needle,"'copy D:\\\\TRACE606.EXE C:\\\\xwn606-kit\\\\TRACE606.EXE','if errorlevel 1 goto fail',"+needle)
p.write_text(s,encoding='utf-8',newline='\n')
old=json.loads((K.parent/'rct603/source001.json').read_text());save=old['save'];reference=old['reference']
assert sha(Path(save['path']))==save['sha256'] and sha(Path(reference['path']))==reference['sha256']
image=Image.open(reference['path']).convert('RGB');rgb=image.crop((160,80,620,440)).tobytes();digest=hashlib.sha1(rgb).digest()
(K/'park_reference.h').write_text('/* Hash metadata for exact PC593 reference RGB ROI; no image payload. */\nstatic const BYTE park_digest606[20]={'+','.join(str(v) for v in digest)+'};\n',encoding='utf-8',newline='\n')
(K/'edition.json').write_text('{"fixture":"/mnt/c/xwn606/pc001"}\n')
(K/'.gitattributes').write_text('* -text whitespace=cr-at-eol\n')
(K/'source001.json').write_text(json.dumps(dict(passed=True,sources=sources,save=save,reference=reference,roi=[160,80,620,440],roi_rgb_sha1=digest.hex(),physical_access=False,game_instrumentation=True),indent=2)+'\n')
print('606 composed; exact retained save/reference and qualified source parents')
