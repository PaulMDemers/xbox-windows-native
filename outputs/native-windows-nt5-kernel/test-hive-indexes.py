"""Exercise hivex's actual new-key format and verify logical hive preservation."""
import hashlib,json,pathlib,struct,sys,tempfile
out=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages')
import hivex
from nt5_hive_indexes import normalize
original=(out.parent/'native-windows-nt5/installed-files/WINNT/system32/config/system').read_bytes()
unchanged,report=normalize(original)
assert unchanged==original and not report['converted']
def logical(path):
 h=hivex.Hivex(str(path));result={}
 def visit(node,path):
  values={h.value_key(v):(h.value_type(v)[0],h.value_value(v)[1].hex()) for v in h.node_values(node)}
  result[path]=values
  for child in h.node_children(node):visit(child,path+'\\'+h.node_name(child))
 visit(h.root(),'');return result
with tempfile.TemporaryDirectory(prefix='nt5-hive-index-test-') as directory:
 p=pathlib.Path(directory)/'SYSTEM';p.write_bytes(original)
 h=hivex.Hivex(str(p),write=True)
 parent=h.node_add_child(h.root(),'NT5IndexRegression')
 for name in ['Alpha','Bravo','Zulu','device0']:
  child=h.node_add_child(parent,name)
  h.node_set_value(child,{'key':'sample','t':4,'value':struct.pack('<I',123)})
 h.commit(str(p));del h
 before=logical(p);serialized=p.read_bytes();converted,report=normalize(serialized)
 assert report['converted'] and converted!=serialized
 p.write_bytes(converted);after=logical(p)
 assert before==after
 again,second=normalize(converted);assert again==converted and not second['converted']
 semantic=hashlib.sha256(json.dumps(after,sort_keys=True).encode()).hexdigest()
result={'passed':['original hive unchanged','new hashed leaf converted','all key paths/types/data preserved','conversion idempotent'],'logical_sha256':semantic,'conversion':report}
(out/'hive-index-tests.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
