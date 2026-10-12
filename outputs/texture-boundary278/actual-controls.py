"""Post-run mutations of copies only; never changes frozen observations."""
import hashlib,json,struct
from pathlib import Path
import proof,decode
k=Path(__file__).resolve().parent;out=k/'emu001';root=Path('E:/xwn278/emu001');dest=out/'actual-controls.json';assert not dest.exists()
t=json.loads((out/'trace.json').read_text());qualified=json.loads((out/'reuse-proof.json').read_text());assert qualified['scoped_unchanged_guest_reuse_passed']
graphs=[proof.load_pages(out,t,key,stage,180000) for stage,key in [(1,'initial'),(2,'terminal')]]
allocations=t['checkpoints'][0]['state_header'][10:14];graph_rejections=0;pixel_rejections=0
for stage,rows in enumerate(graphs,1):
    assert decode.validate_graph(rows,stage,allocations)['full_graph_and_native_allocations_linked']
    for i,r in enumerate(rows):
        columns={64:[2,3,4,5,6],65:[2,3,4,5],66:[2,3,4,5,6,7],67:[4,5,6,7],68:[2,3,4,5,6],69:[2,3,4,5,6,7],70:[2,3,4,5,6,7]}.get(r[0],[])
        for col in columns:
            m=rows.copy();m[i]=r.copy();m[i][col]^=1
            try:decode.validate_graph(m,stage,allocations)
            except (AssertionError,KeyError):graph_rejections+=1
            else:raise AssertionError(('Actual graph mutation accepted',stage,r[0],col))
worker=proof.numbers(t['initial_report'])['worker'];context=int(qualified['graphs'][0]['extension']['native_contexts']['1'])
hashes={}
for u in range(4):
    for stage in range(2):
        p=root/f'watch/unit-{u}-stage-{stage}.bin';data=p.read_bytes();hashes[str(p)]=hashlib.sha256(data).hexdigest()
        h=struct.unpack_from('<24Q',data);start=192+h[18]
        proof.snapshot(data,u,stage,allocations[u]+256,worker,context)
        for index in range(start,len(data)):
            mutant=bytearray(data);mutant[index]^=1
            try:proof.snapshot(bytes(mutant),u,stage,allocations[u]+256,worker,context)
            except AssertionError:pixel_rejections+=1
            else:raise AssertionError(('Actual source/RGBA mutation accepted',u,stage,index))
for name,digest in hashes.items():assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==digest
r=dict(passed=True,post_run_analysis_only=True,actual_graph_mutations_rejected=graph_rejections,
       actual_source_RGBA_byte_mutations_rejected=pixel_rejections,original_files_unchanged=True,
       script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),private_input_hashes=hashes,
       strict_disk_gate_unchanged=False)
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({a:b for a,b in r.items() if a!='private_input_hashes'},indent=2))
