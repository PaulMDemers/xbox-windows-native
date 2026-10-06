"""Pin source/disassembly context for the older stall; do not infer a runtime lock owner."""
import hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent
root=Path('/home/paul/xbox-windows-native/build/fatx-paging-eof-001/source')
assert subprocess.check_output(['git','-C',str(root),'write-tree'],text=True).strip()=='873d6b4ff9505e71da119abd99aba301013e1749'
subprocess.run(['git','-C',str(root),'diff','--quiet'],check=True)
layout=json.loads((k/'fatx-layouts.json').read_text())
old=k.parent/'shutdown-installer-windows/001/timeout-threads.json'
snapshot=json.loads(old.read_text())
rows=[]
for process in snapshot['processes']:
    for thread in process['threads']:
        for item in thread['stack_code_candidates']:
            if item['candidate'] in ['xwnfatx.sys+0x20ae','xwnfatx.sys+0x1942','xwnfatx.sys+0xdb63']:
                rva=int(item['candidate'].split('+')[1],16)
                name=max((n for n,v in layout['symbols'].items() if v<=rva),key=lambda n:layout['symbols'][n])
                rows.append(dict(process=process['image'],thread=thread['thread'],state=thread['state'],
                    stack_candidate=item,function=name,function_offset=rva-layout['symbols'][name],
                    interpretation='Candidate immediately after DirResource acquisition; no unwind or resource-address/owner proof.'))
files={}
for name in ['flush.c','cleanup.c','create.c','dir.c','finfo.c','rw.c']:
    p=root/'drivers/filesystems/vfatfs'/name
    lines=p.read_text().splitlines()
    files[name]=dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),lock_lines=[dict(line=i+1,text=l.strip()) for i,l in enumerate(lines) if ('Resource' in l and any(v in l for v in ['ExAcquire','ExRelease','Resource =']))])
r=dict(scope=__doc__,driver_sha256=layout['driver_sha256'],source_tree='873d6b4ff9505e71da119abd99aba301013e1749',
       snapshot_sha256=hashlib.sha256(old.read_bytes()).hexdigest(),source_files=files,stack_candidates=rows,
       hypothesis='Conflicting Main/Dir lock acquisition orders warrant a controlled concurrent cleanup/flush test.',
       established_runtime_cycle=False,driver_changed=False,
       limits='Same-resource identity, ownership and liveness were not preserved in the older capture. Exception leaks, cache-manager synchronization and other causes are not excluded. Source observations alone do not justify a narrow cleanup-only fix.')
(k/'lock-review.json').write_text(json.dumps(r,indent=2)+'\n');print('Source and old-stack review pinned; runtime ownership remains unknown')
