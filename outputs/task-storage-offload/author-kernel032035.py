"""Author narrow verified offload from the reviewed029/031 protocol."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];old=k/'Offload-Kernel029031.ps1';dest=k/'Offload-Kernel032035.ps1';assert not dest.exists()
names=['nt5-kernel-032','nt5-kernel-035'];pins={n:{key:hashlib.sha256((ws/'work/runs'/n/(key+'.json')).read_bytes()).hexdigest() for key in ['cleanup','instance']} for n in names}
text=old.read_text().replace('manifest-kernel029031-20261010.json','manifest-kernel032035-20261010.json').replace("$names=@('nt5-kernel-029','nt5-kernel-031')","$names=@('nt5-kernel-032','nt5-kernel-035')")
start=text.index('$pinmap=@{');end=text.index('\n$records=@()',start)
replacement='$pinmap=@{\n'+''.join(" '%s'=@{cleanup='%s';instance='%s'}\n"%(n,pins[n]['cleanup'],pins[n]['instance']) for n in names)+'}'
text=text[:start]+replacement+text[end:];text=text.replace('kernel029/031','kernel032/035')
dest.write_text(text,encoding='utf-8',newline='\n')
p=k/'author-kernel032035.json';assert not p.exists();p.write_text(json.dumps({'scope':__doc__,'donor_sha256':hashlib.sha256(old.read_bytes()).hexdigest(),'pins':pins,'new_script_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'closed_only':True,'standalone_header_required':True,'original_paths_retained':True},indent=2)+'\n')
