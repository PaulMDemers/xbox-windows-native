"""MIT. Remove only the interrupted runner's exact temporary registry subtree offline."""
import hashlib,json,shutil,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'work/python-packages'));sys.path.insert(0,str(K.parent/'clean-media404'))
from hive_audit004 import audit
from Registry import Registry
from raw_value004 import stored_value
sys.path.insert(0,str(K.parent/'native-windows-nt5-kernel'));from nt5_hive_indexes import normalize
import hivex
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
host=lambda p:Path('/mnt/'+p[0].lower()+p[2:].replace(chr(92),'/'))
col=read(K/'collection001.json');st=read(K/'stage001.json');assert col['completed'] and col['hook_removed']
n='/E/winnt/system32/config/software';source=host(col['files'][n]['path']);before=host(st['before'][n]['path'])
assert sha(source)==col['files'][n]['sha256'] and sha(before)==st['before'][n]['sha256']
root='Fish Technology Group';target=root+'\\RollerCoaster Tycoon Setup'
def tree(path):
    data=path.read_bytes();r=Registry.Registry(str(path));todo=[('',r.root())];keys=set();values={}
    while todo:
        name,node=todo.pop();keys.add(name)
        for v in node.values():
            t,b=stored_value(data,v._vkrecord.offset());values[(name,v.name() if v._vkrecord.has_name() else '')]=(t,b)
        todo.extend((name+'\\'+s.name(),s) for s in node.subkeys())
    return keys,values
bkeys,bvals=tree(before);keys,vals=tree(source)
assert '\\'+root not in bkeys
scope={'\\'+root,'\\'+target}
assert {p for p in keys if p=='\\'+root or p.startswith('\\'+root+'\\')}==scope
assert {k:v for k,v in vals.items() if k[0] in scope}=={
    ('\\'+target,'Path'):(1,('C:\\xwn586-kit\\game\0').encode('utf-16le')),
    ('\\'+target,'SetupPath'):(1,('C:\\xwn586-kit\\game\0').encode('utf-16le')),
    ('\\'+target,'Language'):(4,b'\0\0\0\0')}
assert audit(source)['clean']
dest=Path('/mnt/c/xwn596/registry-cleanup002');assert not dest.exists()
assert shutil.disk_usage('/mnt/c').free-32*1024**2>=20*1024**3
dest.mkdir();raw=dest/'software-hivex';candidate=dest/'software'
h=hivex.Hivex(str(source),write=True);node=h.node_get_child(h.root(),root);assert node
h.node_delete_child(node);h.commit(str(raw));del h
fixed,conversion=normalize(raw.read_bytes());candidate.write_bytes(fixed)
afterkeys,aftervals=tree(candidate)
assert afterkeys==keys-scope and aftervals=={k:v for k,v in vals.items() if k[0] not in scope}
review=audit(candidate);assert review['clean'] and review['header_valid'] and review['independent_raw_values_agree'] and review['typed_decode_errors']==audit(source)['typed_decode_errors']
assert sha(source)==col['files'][n]['sha256']
r=dict(passed=True,source=col['files'][n],candidate=dict(path='C:/xwn596/registry-cleanup002/software',bytes=candidate.stat().st_size,sha256=sha(candidate)),removed_keys=sorted(scope),removed_value_count=3,all_other_key_names_and_raw_values_unchanged=True,independent_audit=review,normalization=conversion,physical_writes=False,typed_decode_limitation='Pre-existing Microsoft/DRM DataPath type1004 remains identically undecoded; independent full raw maps and exact error entries agree before/after.',source_sha256=sha(__file__),limits='Narrow restoration of temporary game setup subtree; preserves other post-run registry state, events and saved games. No driver modification or runtime validation claim.')
out=K/'cleanup-preparation002.json';assert not out.exists();out.write_text(json.dumps(r,indent=2)+'\n');print('Prepared exact subtree cleanup; independent hive readers agree')
