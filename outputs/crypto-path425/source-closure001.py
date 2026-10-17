"""Read-only match of the installed FATX binary and its recorded403 source tree."""
import hashlib,json,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];out=K/'source-closure001.json';assert not out.exists()
sha=lambda b:hashlib.sha256(b).hexdigest()
build=json.loads((W/'outputs/release-readiness403/compiled-records001/fatx/build.json').read_text())
tree=build['source']['tree'];source=Path('/home/paul/xbox-windows-native/release-readiness403-fatx001/source')
records=[]
for name in ['dirwr.c','create.c']:
    path='drivers/filesystems/vfatfs/'+name
    blob=subprocess.check_output(['git','-C',str(source),'show',tree+':'+path])
    live=(source/path).read_bytes();public=(W/'src/drivers/fatx'/path).read_bytes()
    assert blob==live==public
    records.append({'path':path,'sha256':sha(blob),'recorded_tree_and_public_source_exact':True})
files=json.loads(Path('/mnt/e/xwn425/cold1/after/files.json').read_text())
artifact=build['artifacts'][0];matches=[n for n,h in files.items() if n.endswith('/'+artifact['file']) and h==artifact['sha256']];assert len(matches)==1
text=(source/'drivers/filesystems/vfatfs/dirwr.c').read_text()
assert 'if (DirContext.LongNameU.Length / sizeof(WCHAR) > 42)' in text and 'if (NameA.Length == 0 || NameA.Length > 42)' in text
record={'passed':True,'source_tree':tree,'sources':records,'installed_file':matches[0],'installed_sha256':artifact['sha256'],
        'scope':'Static matching source returns STATUS_NAME_TOO_LONG at encoded/name-length entry guards; native syscall return observed separately. No internal driver instruction breakpoint claimed.'}
out.write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record))
