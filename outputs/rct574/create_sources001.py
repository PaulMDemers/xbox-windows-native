"""MIT. Fresh screenshot control; no prior runtime reopened."""
from pathlib import Path
K=Path(__file__).resolve().parent;old=K.parent/'rct573'
for name in ['runner.c','input.h','title_signature.h','build001.py','media001.py','review_media001.py','prepare002.py','vm.py','cold002.py','login001.py','collect001.py','review001.py','capture_review001.py','input_review001.py','edition.json','.gitattributes']:
    dest=K/name;assert not dest.exists();dest.write_bytes((old/name).read_text().replace('573','574').encode())
p=K/'input.h';s=p.read_text()
s=s.replace('static BOOL capture(const char* tag){','static BOOL gamecapture(const char* tag);\nstatic BOOL capture(const char* tag){')
s=s.replace(' if(capturecount>=32||!state(tag)', ' if(tag[0]==\'f\'&&tag[1]==\'u\'&&tag[2]==\'l\'&&tag[3]==\'l\')return gamecapture(tag);\n if(capturecount>=32||!state(tag)')
s=s.replace('static BOOL scrollcases(', '#include "game_capture.h"\nstatic BOOL scrollcases(',1)
s=s.replace('if(!reacquire("fullscreen_reacquire")||!capture("full-options")||!click(292,39))return FALSE;', '''if(!reacquire("fullscreen_reacquire"))return FALSE;
 number("fullscreen_no_gdi_begin_tick",GetTickCount());Sleep(20000);
 if(!state("full-options-passive")||!click(292,39))return FALSE;''')
p.write_bytes(s.encode())
p=K/'build001.py';s=p.read_text().replace("shutil.copyfile(K/'title_signature.h',O/'title_signature.h')","shutil.copyfile(K/'title_signature.h',O/'title_signature.h');shutil.copyfile(K/'game_capture.h',O/'game_capture.h')");p.write_bytes(s.encode())
p=K/'prepare002.py';s=p.read_text().replace("K/'title_signature.h',K/'edition.json'","K/'title_signature.h',K/'game_capture.h',K/'edition.json'");p.write_bytes(s.encode())
p=K/'vm.py';s=p.read_text().replace('capture=time.monotonic()+45','capture=time.monotonic()+5');p.write_bytes(s.encode())
p=K/'input_review001.py';s=p.read_text().replace("'mode-menu','full-options','full-before'","'mode-menu','full-before'").replace('list(range(16))','list(range(15))');p.write_bytes(s.encode())
