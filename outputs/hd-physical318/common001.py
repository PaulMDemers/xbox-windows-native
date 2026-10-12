"""Owned physical318 scope; baseline256 identity/ticket/FTP behavior retained."""
import importlib.util,json,pathlib,sys,hashlib,os,time,ftplib
k=pathlib.Path(__file__).resolve().parent;canonical=k.parents[1]
path=canonical/'outputs/demo-audio-level256/common001.py'
spec=importlib.util.spec_from_file_location('baseline256',path);c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
sys.path.insert(0,str(k.parent/'surface-bridge260'));from atomic_json import write_json
read=c.read;sha=c.sha;utc=c.utc;save=write_json;ticket=c.ticket;connect=c.connect;get=c.get;put=c.put;keep=c.keep;names=c.names;startup=c.startup
def incoming(path):
 r=read(k/'capture001.json');data=(k/'artifacts/before001'/path.lstrip('/')).read_bytes()
 assert sha(data)==r['files'][path]['sha256'];return data
def fixed():return c.fixed()
def check_fixed(f,staged=False):
 expected=dict(fixed())
 if staged:expected.update({v['path']:v['sha256'] for v in read(k/'package.json')['video']})
 result={p:sha(get(f,p))==h for p,h in expected.items()};assert all(result.values()),'Protected baseline mismatch';return result
def pins():
 ticket()
 for name,h in read(k/'frozen.json').items():assert sha(pathlib.Path(name).read_bytes())==h,name
