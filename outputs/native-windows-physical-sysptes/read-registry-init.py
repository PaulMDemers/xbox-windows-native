from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages');import hivex
kit=Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/native-windows-physical-sysptes');f=kit/'package/WINNT/system32/config/system';h=hivex.Hivex(str(f))
def value(path,name):
 n=h.root()
 for part in path.split('\\'):
  n=h.node_get_child(n,part)
  if not n:return None
 v=next((v for v in h.node_values(n) if h.value_key(v).lower()==name.lower()),None)
 if not v:return None
 t,b=h.value_value(v);return {'type':t,'bytes':b.hex()}
items={}
for path,name in [('Select','Current'),('ControlSet001\\Control\\Nls\\Language','Default'),('ControlSet001\\Control\\Nls\\Language','InstallLanguage'),('ControlSet001\\Control\\ProductOptions','ProductSuite'),('ControlSet001\\Control\\Session Manager\\Memory Management','VerifyDrivers')]:items[path+'\\'+name]=value(path,name)
r={'hive_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'values':items};(kit/'registry-init-inputs.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
