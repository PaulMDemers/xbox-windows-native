import json, subprocess
from pathlib import Path
root=Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility')
base=Path('/home/paul/xbox-windows-native/build')
results=[]
for name in ['framebuffer','loader','display','launcher','audio']:
    output=base/('public-layout402-'+name+'001')
    command=['python3','-B',str(root/'tools/xwn.py'),'build','--profile',name,'--output',str(output)]
    if name=='launcher':
        command+=['--cache','/home/paul/xbox-windows-native/sources/cromwell','--gcc12','/usr/bin/gcc-12']
    else:
        command+=['--cache','/home/paul/xbox-windows-native/sources/reactos-extended','--rosbe','/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1']
    print('START',name,flush=True)
    result=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=1500)
    (root/'outputs/public-layout402'/('build-'+name+'001-console.txt')).write_text(result.stdout)
    results.append({'profile':name,'exit_code':result.returncode,'output':str(output)})
    print('FINISHED',name,result.returncode,flush=True)
    if result.returncode:
        print(result.stdout[-3000:],flush=True)
    (root/'outputs/public-layout402/build-batch001.json').write_text(json.dumps(results,indent=2)+'\n')
