"""Reuse the owned first-phase harness; two-boot lifecycle is separate."""
from pathlib import Path
import json
K=Path(__file__).resolve().parent;old=K.parent/'rct584'
for n in ['vm.py','login001.py','cold002.py','collect001.py','review001.py','input_transport001.py','edition.json']:
    p=K/n;assert not p.exists()
    p.write_text((old/n).read_text().replace('584','585').replace('xwn582','xwn585'))
p=K/'prepare001.py';assert not p.exists()
s=(old/'prepare003.py').read_text().replace('584','585')
s=s[:s.index("r['inputs'].update")]+s[s.index("out.write_text"):]
s=s.replace("print('Prepared fresh585, exact582 helper/media')","print('Prepared fresh585 phase1; overall experiment OPEN for planned second boot')")
p.write_text(s)
p=K/'experiment001.json';assert not p.exists()
p.write_text(json.dumps(dict(overall_closed=False,planned_phases=['save and normal restart','load same cold-pinned save after normal restart'],physical_access=False,phase1_started=False,phase2_admitted=False,closed_runtime_parent=False,notes='Each process closes normally; experiment remains OPEN across the preplanned second boot. Never reopen584 or another closed fixture.'),indent=2)+'\n')
