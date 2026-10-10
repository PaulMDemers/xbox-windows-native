from pathlib import Path
k=Path(__file__).resolve().parent
s=(k.parent/'video-text-oracle206/typed-state.py').read_text().replace("out=k/('emu-'+case)","out=k/case")
(k/'typed-state.py').write_text(s)
