"""Host guard tests on actual exported utility functions; no hardware connection."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
from unittest.mock import patch

K=Path(__file__).resolve().parent
def module(name):
    spec=importlib.util.spec_from_file_location(name,K/'public/tools'/name)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
r=module('reconstruct.py');v=module('verify-package.py')
checks=[]
def refuses(name, action):
    try: action()
    except (ValueError,FileNotFoundError): checks.append(name);return
    raise AssertionError('Expected refusal: '+name)
with tempfile.TemporaryDirectory() as tmp:
    root=Path(tmp)/'pkg';root.mkdir();p=root/'patch.patch';p.write_text('patch data')
    original=dict(name='test',base_commit='a'*40,result_tree='b'*40,patch='patch.patch',
                  patch_sha256=hashlib.sha256(p.read_bytes()).hexdigest())
    def component(**changes):
        data=dict(original,**changes)
        (root/'components.json').write_text(json.dumps({'components':[data]}))
    r.ROOT=root
    component();assert r.load_component('test')[0]==original;checks.append('valid component')
    refuses('unknown component',lambda:r.load_component('other'))
    component(patch_sha256='0'*64);refuses('changed patch bytes',lambda:r.load_component('test'))
    component(result_tree='--help');refuses('invalid Git identity',lambda:r.load_component('test'))
    outside=Path(tmp)/'outside.patch';outside.write_text('patch data')
    component(patch='../outside.patch');refuses('patch escapes package',lambda:r.load_component('test'))
    component()
    cache=Path(tmp)/'cache';cache.mkdir()
    refuses('existing output',lambda:r.reconstruct('test',cache,cache))
    refuses('cache descendant output',lambda:r.reconstruct('test',cache,cache/'child'))
    refuses('package descendant output',lambda:r.reconstruct('test',cache,root/'child'))
    with patch.object(r.shutil,'disk_usage',return_value=type('Disk',(),{'free':1})()):
        refuses('space reserve',lambda:r.reconstruct('test',cache,Path(tmp)/'new'))
    # Separate minimal manifest package exercises exact bytes and namespace checks.
    sample=Path(tmp)/'manifest';sample.mkdir();(sample/'one.txt').write_bytes(b'original')
    entry=dict(path='one.txt',bytes=8,sha256=hashlib.sha256(b'original').hexdigest())
    def manifest(entries): (sample/'MANIFEST.json').write_text(json.dumps({'files':entries}))
    manifest([entry]);assert v.verify(sample)['verified_files']==1;checks.append('exact manifest')
    (sample/'one.txt').write_bytes(b'modified');refuses('manifest changed bytes',lambda:v.verify(sample))
    (sample/'one.txt').write_bytes(b'original');(sample/'extra.txt').write_text('extra')
    refuses('unlisted file',lambda:v.verify(sample));(sample/'extra.txt').unlink()
    manifest([entry,entry]);refuses('duplicate path',lambda:v.verify(sample))
    manifest([dict(entry,path='../outside.patch')]);refuses('manifest path escape',lambda:v.verify(sample))
out=K/'tool-tests001.json'
with out.open('x') as f:json.dump({'passed':True,'checks':checks,'count':len(checks),
    'scope':'Actual tool guards with synthetic local inputs; no reconstruction/compiler/FTP in these tests'},f,indent=2)
print(json.dumps({'passed':True,'checks':len(checks)}))
