"""Inventory a private NTFS image through the installed read-only ntfsls tool."""
import argparse,json,os,pathlib,re,subprocess
p=argparse.ArgumentParser();p.add_argument('partition',type=pathlib.Path);p.add_argument('output',type=pathlib.Path);a=p.parse_args()
runtime=pathlib.Path('/home/paul/xbox-windows-native/toolchains/offline-disk/root')
env=dict(os.environ,LD_LIBRARY_PATH=str(runtime/'usr/lib/x86_64-linux-gnu'))
raw=subprocess.check_output([str(runtime/'usr/bin/ntfsls'),'-f','-i','-l','-R',str(a.partition)],env=env)
text=raw.decode('utf-8');dirs=[];files=[];parent=None
for line in text.splitlines():
 if line.endswith(':') and line.startswith('/'):
  parent=line[:-1];dirs.append(parent);continue
 if not line.strip():continue
 m=re.match(r'^\s*(\d+)\s+(\d+)\s+[A-Za-z]{3}\s+\d+\s+\d\d:\d\d\s+\d{4} (.+)$',line)
 assert m and parent is not None,line
 if m[3] in ('.','..'):continue
 files.append({'path':parent.rstrip('/')+'/'+m[3],'inode':int(m[1]),'bytes':int(m[2])})
directory_set=set(dirs);files=[f for f in files if f['path'] not in directory_set]
long=[f for f in files if any(len(c)>42 for c in f['path'].split('/'))]
nonascii=[f for f in files if not f['path'].isascii()]
a.output.write_text(json.dumps({'directories':dirs,'files':files,'overlong':long,'nonascii':nonascii},indent=2)+'\n')
print(len(dirs),'directories',len(files),'files')
