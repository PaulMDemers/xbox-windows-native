"""Adapt qualified CD transport, adding only the pinned PC593 save."""
from pathlib import Path
K=Path(__file__).resolve().parent;S=K.parent/'rct602'
for name in ['media001.py','media_review001.py']:
 text=(S/name).read_text(encoding='utf-8')
 for a,b in [('xwn602','xwn603'),('XWN602','XWN603'),('RUN602','RUN603'),('VERIFY602','VERIFY603')]:text=text.replace(a,b)
 if name=='media001.py':
  old="for row in b['rows']:";assert old in text
  text=text.replace(old,"extra=json.loads((K/'source001.json').read_text())['save'];saved=Path(extra['path']);assert sha(saved)==extra['sha256'];add('game/Saved Games/XWN593.SV4',saved)\n"+old)
  old="'copy D:\\\\TRACE602.EXE C:\\\\xwn603-kit\\\\TRACE602.EXE','if errorlevel 1 goto fail',";assert old in text;text=text.replace(old,'')
 else:
  text=text.replace("set(mapping['mapped_files'])|set(mapping['supplemental_files'])==set(a)","set(mapping['mapped_files'])|set(mapping['supplemental_files'])|{'game/Saved Games/XWN593.SV4'}==set(a)")
 assert not (K/name).exists();(K/name).write_text(text,encoding='utf-8',newline='\n')
print('603 media source created; retained save added and debugger tool removed')
