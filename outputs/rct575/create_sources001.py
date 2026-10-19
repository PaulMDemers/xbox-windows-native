"""MIT. Fresh notification-settling control; never reopen a closed runtime."""
from pathlib import Path
K=Path(__file__).resolve().parent;old=K.parent/'rct574'
for name in ['runner.c','input.h','game_capture.h','title_signature.h','build001.py','media001.py','review_media001.py','prepare002.py','vm.py','cold002.py','login001.py','collect001.py','review001.py','capture_review001.py','input_review001.py','display_review001.py','edition.json','.gitattributes']:
    dest=K/name;assert not dest.exists()
    dest.write_bytes((old/name).read_text().replace('574','575').encode())
p=K/'game_capture.h';s=p.read_text()
old=' if(ok)ok=state("screenshot_done");'
new=' if(ok){number("screenshot_settle_begin",GetTickCount());Sleep(10000);number("screenshot_settle_end",GetTickCount());ok=state("screenshot_done");}'
assert s.count(old)==1;s=s.replace(old,new);p.write_bytes(s.encode())
# Preserve more precise capture failure timestamps in this new supervisor.
p=K/'vm.py';s=p.read_text().replace("state['capture_error']=type(e).__name__", "state.setdefault('capture_errors',[]).append(dict(error=type(e).__name__,utc=utc(),process_exit=proc.poll()))")
p.write_bytes(s.encode())
