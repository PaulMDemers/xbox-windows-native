"""Run the portable reconstruction CLI using independent fresh object stores."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

K=Path(__file__).resolve().parent
ROOT=Path('/mnt/c/xwn401/source003')
OUT=Path('/mnt/c/xwn401/reconstruct001')
if sys.platform!='linux' or OUT.exists():raise RuntimeError('Fresh Linux validation directory required')
OUT.mkdir()
components=json.loads((ROOT/'components.json').read_text())['components']
rows=[]
for c in components:
    cache='/home/paul/xbox-windows-native/sources/'+('cromwell' if c['name'].startswith('launcher') else 'reactos-extended')
    output=OUT/c['name']
    command=[sys.executable,'-B',str(ROOT/'tools/reconstruct.py'),'--component',c['name'],
             '--source-cache',cache,'--output',str(output)]
    # Exercise full file materialization on the smaller Cromwell tree. ReactOS
    # verification uses full independent object stores/indexes, not an archive subset.
    if not c['name'].startswith('launcher'):command.append('--index-only')
    with (OUT/(c['name']+'.log')).open('x') as log:
        subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
    report=json.loads((output/'reconstruction-report.json').read_text())
    if report['actual_tree']!=c['result_tree']:raise RuntimeError('Wrong result tree')
    if (output/'.git/objects/info/alternates').exists():raise RuntimeError('Unexpected shared object store')
    if c['name']=='audio004':
        rule=c['checkout_byte_rules'][0]
        subprocess.run(['git','-C',str(output),'checkout-index','--',rule['path']],check=True)
        if hashlib.sha256((output/rule['path']).read_bytes()).hexdigest()!=rule['checked_out_sha256']:
            raise RuntimeError('Actual Git checkout does not match pinned audio INF bytes')
        report['actual_inf_checkout_verified']=True
    rows.append(report)
    print(c['name'],'portable CLI verified',flush=True)
with (K/'portable-replay001.json').open('x') as f:
    json.dump({'passed':True,'components':rows,'source_shared_objects':False,'compiled':False,
               'physical_access':False,'fresh_output':str(OUT)},f,indent=2)
