"""MIT. Independently compare game registry subtree before/after physical run."""
import json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'work/python-packages'));from Registry import Registry
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
before=read(K/'stage001.json');after=read(K/'collection001.json');assert after['completed'] and after['hook_removed']
def tree(path):
 r=Registry.Registry(path)
 try:k=r.open('Fish Technology Group')
 except Registry.RegistryKeyNotFoundException:return None
 def walk(key):return dict(values={v.name():dict(type=v.value_type(),value=v.value()) for v in key.values()},children={c.name():walk(c) for c in key.subkeys()})
 return walk(k)
n='/E/winnt/system32/config/software';a=tree(before['before'][n]['path']);b=tree(after['files'][n]['path']);assert a==b,'Game registry subtree not restored'
out=K/'registry-review001.json';assert not out.exists();out.write_text(json.dumps(dict(passed=True,game_registry_subtree_restored=True,console_writes=False,scope='Exact typed game-subtree comparison from independently collected hives; full hive/events audited separately'),indent=2)+'\n');print('Game registry subtree restored exactly')
