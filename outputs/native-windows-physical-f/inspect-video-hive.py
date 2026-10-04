import pathlib,sys,json,struct
k=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/native-windows-physical-f');sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages');import hivex
import argparse
p=argparse.ArgumentParser();p.add_argument('--input',type=pathlib.Path,default=k/'artifacts/physical-b4-system');p.add_argument('--output',type=pathlib.Path,default=k/'physical-b4-video-registry.json');a=p.parse_args()
h=hivex.Hivex(str(a.input));result={}
def walk(n,path):
 vals={}
 for v in h.node_values(n):
  t,d=h.value_value(v);vals[h.value_key(v)]=int.from_bytes(d,'little') if t==4 else d.decode('utf-16le',errors='replace').rstrip('\0') if t in (1,2,7) else d.hex()
 result[path]=vals
 for ch in h.node_children(n):walk(ch,path+'\\'+h.node_name(ch))
def node(path):
 n=h.root()
 for part in path.split('\\'):
  n=h.node_get_child(n,part)
  if not n:return 0
 return n
for p in ['Select','ControlSet001\\Services\\XboxVnt5','ControlSet001\\Control\\Video','ControlSet001\\Control\\Class\\{4D36E968-E325-11CE-BFC1-08002BE10318}']:
 n=node(p)
 if n:walk(n,p)
p='ControlSet001\\Enum\\PCI';n=node(p)
for ch in h.node_children(n):
 if 'DEV_02A0' in h.node_name(ch).upper():walk(ch,p+'\\'+h.node_name(ch))
a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
