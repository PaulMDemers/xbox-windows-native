import json,sys
from pathlib import Path
sys.path.insert(0,"/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages")
import hivex
h=hivex.Hivex("/mnt/c/xwn405/extract004/files/WINNT/system32/config/software")
n=h.root()
for part in ["Microsoft","Windows NT","CurrentVersion","Winlogon"]:n=h.node_get_child(n,part);assert n
values={}
for key in ["DefaultUserName","DefaultDomainName","DefaultPassword"]:
 v=h.node_get_value(n,key)
 if v:values[key]=h.value_string(v)
p=Path("/mnt/c/xwn405/logon-private001.json");assert not p.exists();p.write_text(json.dumps(values));p.chmod(0o600)
print(json.dumps({"fields_present":list(values),"password_present":"DefaultPassword" in values,"password_empty":values.get("DefaultPassword")==""}))
