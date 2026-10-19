"""Prepare a fresh attempt using bounded namespace edits, never numeric metadata."""
from pathlib import Path
import hashlib,json,re
K=Path(__file__).resolve().parent;N=K.parent/'rct586';assert not N.exists();N.mkdir()
names=['runner.c','welcome.h','input.h','save_dialog.h','title_signature.h','game_capture.h','verify.c','assets001.py','build001.py','media001.py','media_review001.py','binary_review001.py','vm.py','login001.py','cold002.py','collect001.py','review001.py','input_transport001.py','edition.json','prepare001.py','DESIGN.md']
pins={}
for name in names:
    p=K/name;s=p.read_text();pins[name]=hashlib.sha256(p.read_bytes()).hexdigest()
    s=s.replace('xwn585','xwn586').replace('rct585','rct586').replace('XWN585','XWN586').replace('RUN585','RUN586').replace('VERIFY585','VERIFY586').replace('run585','run586').replace('verify585','verify586')
    s=re.sub(r'(?<![0-9a-fA-F])585(?![0-9a-fA-F])','586',s)
    if name in ['media001.py','binary_review001.py']:s=s.replace('build002','build001')
    (N/name).write_bytes(s.replace('\r\n','\n').replace('\n','\r\n').encode())
# Integrity metadata is generated from the pinned retail bytes, not copied with
# namespace substitution. Independently validate every C row before compilation.
(N/'.gitattributes').write_text('* -text whitespace=cr-at-eol\n')
(N/'source-preparation001.json').write_text(json.dumps(dict(source_pins=pins,metadata_regeneration_required=True,physical_access=False,closed_parent=False),indent=2)+'\n')
(N/'experiment001.json').write_text(json.dumps(dict(overall_closed=False,phase1_started=False,phase2_admitted=False,planned_phases=['save and normal restart','load cold-pinned save'],physical_access=False),indent=2)+'\n')
