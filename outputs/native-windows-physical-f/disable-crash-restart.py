"""Patch only existing inline AutoReboot DWORDs in a clean copied SYSTEM hive."""
import pathlib,sys,json,hashlib,struct,re
k=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/native-windows-physical-f')
sys.path[:0]=['/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages',str(k.parent/'native-windows-fatx-paging')]
import hivex
from importlib.machinery import SourceFileLoader
audit=SourceFileLoader('audit_hive',str(k.parent/'native-windows-fatx-paging/audit-hive.py')).load_module().audit_hive
source=k/'artifacts/physical-system-before-v2';target=k/'artifacts/physical-system-no-auto-reboot';assert not target.exists()
before=source.read_bytes();data=bytearray(before);assert data[:4]==b'regf' and struct.unpack_from('<I',data,4)[0]==struct.unpack_from('<I',data,8)[0]
checksum=0
for v in struct.unpack_from('<127I',data):checksum^=v
assert (0xfffffffe if checksum==0xffffffff else checksum or 1)==struct.unpack_from('<I',data,508)[0]
h=hivex.Hivex(str(source));changes=[]
for cs in h.node_children(h.root()):
 name=h.node_name(cs)
 if not re.fullmatch(r'ControlSet\d{3}',name):continue
 n=h.node_get_child(h.node_get_child(cs,'Control'),'CrashControl');assert n
 v=h.node_get_value(n,'AutoReboot');assert v
 kind,old=h.value_value(v);assert kind==4 and old in (bytes(4),b'\x01\0\0\0')
 assert data[v+4:v+6]==b'vk' and struct.unpack_from('<I',data,v+8)[0]==0x80000004 and bytes(data[v+12:v+16])==old
 data[v+12:v+16]=bytes(4);changes.append({'control_set':name,'cell_offset':v,'data_offset':v+12,'old':int.from_bytes(old,'little'),'new':0})
assert changes
allowed={i for c in changes for i in range(c['data_offset'],c['data_offset']+4)}
assert all(i in allowed for i,(x,y) in enumerate(zip(before,data)) if x!=y)
target.write_bytes(data);del h
h=hivex.Hivex(str(target))
for c in changes:
 n=h.node_get_child(h.root(),c['control_set']);n=h.node_get_child(h.node_get_child(n,'Control'),'CrashControl');assert h.value_value(h.node_get_value(n,'AutoReboot'))==(4,bytes(4))
r={'source_sha256':hashlib.sha256(before).hexdigest(),'target_sha256':hashlib.sha256(data).hexdigest(),'changes':changes,'only_existing_inline_dwords_changed':True,'before_audit':audit(source),'after_audit':audit(target)}
(k/'crash-restart-setting.json').write_text(json.dumps(r,indent=2)+'\n');print(r['changes'])
