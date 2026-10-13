from pathlib import Path
p=Path(__file__).resolve().parent
assert not (p/'host002.c').exists() and not (p/'host002.py').exists()
s=(p/'host.c').read_text();assert s.count('a[i]=(unsigned char)rnd(256)')==1
s=s.replace('a[i]=(unsigned char)rnd(256)','{seed=seed*1664525U+1013904223U;a[i]=(unsigned char)(seed>>24);}')
(p/'host002.c').write_text(s)
s=(p/'host.py').read_text().replace('host001','host002').replace("['primary_copy.c','primary_plan.h','host.c','host.py']","['primary_copy.c','primary_plan.h','host002.c','host002.py']").replace("out/'host.c'","out/'host002.c'")
(p/'host002.py').write_text(s)
