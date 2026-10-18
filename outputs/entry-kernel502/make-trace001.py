"""Retain reviewed read-only transport/capture helpers; append new entry trace."""
from pathlib import Path
K=Path(__file__).resolve().parent;src=(K.parent/'busy-handoff471/trace001.py').read_text()
prefix=src[:src.index('\nsave()\ntry:')]
prefix=prefix.replace('from marker_decode import success','from contracts import plan,arguments,returned\nfrom entry_decode import decode as decode_entry')
prefix=prefix.replace('xwn471','xwn502').replace('nt5-busy471','nt5-entry502').replace('5714','6024').replace('5715','6025')
prefix=prefix.replace("build=json.loads((K/'build001.json').read_text())", "build=json.loads((K.parent/'entry-launch499/build001.json').read_text())")
prefix=prefix.replace("sym=build['wrapper_symbols'];stub=build['stub_symbols']", "sym=build['wrapper_symbols']")
prefix=prefix.replace("review=json.loads((K/'source-review001.json').read_text());assert review['passed']", "assert json.loads((K/'host001.json').read_text())['passed']")
prefix=prefix.replace("Path('C:/xwn502/build001/default.xbe')", "Path('C:/xwn499/build001/default.xbe')")
prefix=prefix.replace("payload=xbe[0x3000:0x3000+build['payload_bytes']]", "calls=plan(xbe,sym)")
(K/'trace001.py').write_bytes((prefix+(K/'trace-body.txt').read_text()).encode())
(K/'entry_decode.py').write_bytes((K.parent/'entry-receipt498/decode.py').read_bytes())
