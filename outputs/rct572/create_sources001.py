"""MIT. New control with independently revised title reference; no disk reuse."""
from pathlib import Path
K=Path(__file__).resolve().parent;old=K.parent/'rct571'
for name in ['runner.c','input.h','build001.py','media001.py','review_media001.py','prepare002.py','vm.py','cold002.py','login001.py','collect001.py','review001.py','capture_review001.py','input_review001.py','edition.json','.gitattributes']:
    dest=K/name;assert not dest.exists()
    dest.write_bytes((old/name).read_text(encoding='utf-8').replace('571','572').encode())
