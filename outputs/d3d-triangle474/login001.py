"""Use the isolated fixture's own saved logon value, without printing/journaling it."""
import argparse,importlib,json,sys,time
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('/home/paul/xbox-windows-native/d3d-triangle474-pc001')
sys.path.insert(0,str(K.parents[1]/'work/python-packages'));from Registry import Registry
sys.path.insert(0,str(K.parent/'clean-media404'));Qmp=importlib.import_module('pc-run001').Qmp
p=argparse.ArgumentParser();p.add_argument('--phase',type=int,choices=[1],required=True);a=p.parse_args()
out=K/f'ntfs-login{a.phase}.json';assert not out.exists()
state=json.loads((K/f'ntfs-phase{a.phase}.json').read_text());assert not state['closed']
assert f'xwn-d3d-triangle474-pc-phase{a.phase}' in Path(f"/proc/{state['pid']}/cmdline").read_bytes().decode()
r=Registry.Registry(str(P/'cold0-002/files/WINNT/system32/config/software'))
k=r.open('Microsoft\\Windows NT\\CurrentVersion\\Winlogon');assert k.value('DefaultUserName').value()=='Win2K'
secret=k.value('DefaultPassword').value();assert isinstance(secret,str) and 0<len(secret)<64
mapping={'!':'shift-1','@':'shift-2','#':'shift-3','$':'shift-4','%':'shift-5','^':'shift-6','&':'shift-7','*':'shift-8','(':'shift-9',')':'shift-0','-':'minus','_':'shift-minus','.':'dot',' ':'spc'}
keys=[]
for c in secret:
 if 'a'<=c<='z' or '0'<=c<='9':keys.append(c)
 elif 'A'<=c<='Z':keys.append('shift-'+c.lower())
 else:assert c in mapping;keys.append(mapping[c])
record={'phase':a.phase,'source':'Fixture cold Winlogon, same Win2K account','secret_in_record':False,'submitted':False}
out.write_text(json.dumps(record,indent=2)+'\n')
with Qmp(P/f'phase{a.phase}/qmp.sock') as q:
 for key in keys:q.call('human-monitor-command',{'command-line':'sendkey '+key});time.sleep(.12)
 q.call('human-monitor-command',{'command-line':'sendkey ret'})
record['submitted']=True;out.write_text(json.dumps(record,indent=2)+'\n');print('Owned fixture logon submitted; value not printed.')
