"""Preserve failed build001; remove misleading indentation in a new source version."""
from pathlib import Path
K=Path(__file__).resolve().parent
for old,new,a,b in [('load_dialog.h','load_dialog002.h','if(f==INVALID_HANDLE_VALUE)return FALSE;size=','if(f==INVALID_HANDLE_VALUE)return FALSE;\n size='),
 ('input.h','input002.h','"load_dialog.h"','"load_dialog002.h"'),('runner.c','runner002.c','"input.h"','"input002.h"'),
 ('build001.py','build002.py',"'runner.c'","'runner002.c'")]:
 s=(K/old).read_text();assert a in s;s=s.replace(a,b)
 if old=='build001.py':s=s.replace('build001','build002')
 assert not (K/new).exists();(K/new).write_text(s,encoding='utf-8',newline='\n')
for n in ['media001.py','binary_review001.py']:
 p=K/n;s=p.read_text();assert 'build001.json' in s;p.write_text(s.replace('build001.json','build002.json'),encoding='utf-8',newline='\n')
print('New002 sources preserve001 failure and unchanged warning flags')
