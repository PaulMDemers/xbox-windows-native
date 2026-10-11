"""Read closed QCOW metadata and correlate stored raw bytes with host writes."""
import hashlib,importlib.util,json,re,struct,sys
from pathlib import Path
k=Path(__file__).resolve().parent;case=sys.argv[1];assert case in ['emu001','emu002']
out=k/case;run=k.parents[1]/('work/runs/nt5setup-'+case);assert (run/'cleanup.json').exists()
f=json.loads((out/'forensics.json').read_text());data=(run/'hdd.qcow2').read_bytes()
h=struct.unpack_from('>IIQIIQIIQQIIQ',data)
assert h[0]==0x514649fb and h[1]==3 and h[6]==0
assert struct.unpack_from('>Q',data,72)[0]&(1<<4)==0
bits=h[4];cluster=1<<bits;l2bits=bits-3;mask=0x00fffffffffffe00
spec=importlib.util.spec_from_file_location('p',k/'parse-transfer.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
backend=m.records(run/'transfer.backend.bin');trace=(run/'host-io.trace').read_text();lines=trace.splitlines()
part=re.compile(r'^bdrv_co_pwritev_part bs (\S+) offset (\d+) bytes (\d+) flags (\S+)$')
block=re.compile(r'^blk_co_pwritev blk (\S+) bs (\S+) offset (\d+) bytes (\d+) flags (\S+)$')
rows=[]
for name,file in f['files'].items():
    if file.get('absent'):continue
    offset=file['chain'][0]['byte_offset'];size=file['length']
    l1index=offset>>(bits+l2bits);assert l1index<h[7]
    l1=struct.unpack_from('>Q',data,h[8]+l1index*8)[0];l2off=l1&mask
    l2index=(offset>>bits)&((1<<l2bits)-1)
    entry=struct.unpack_from('>Q',data,l2off+l2index*8)[0] if l2off else 0
    candidates=[]
    for i,line in enumerate(lines[:-2]):
        a=block.fullmatch(line)
        if not a or int(a[3])!=offset:continue
        b=part.fullmatch(lines[i+1]);c=part.fullmatch(lines[i+2])
        if b and c and b[1]==a[2] and c[1]!=b[1] and int(b[2])==offset and int(b[3])==int(a[4]):
            child_offset=int(c[2]);child_bytes=int(c[3]);n=int(a[4]);cow=False
            if child_bytes!=n:
                if child_bytes!=cluster or child_offset%cluster or offset%cluster+n>cluster:continue
                child_offset+=offset%cluster;cow=True
            candidates.append(dict(line=i+1,bytes=n,child_file_offset=child_offset,child_request_offset=int(c[2]),child_request_bytes=child_bytes,whole_cluster_cow=cow,root_bs=b[1],child_bs=c[1]))
    row=dict(file=name,virtual_offset=offset,length=size,l1index=l1index,l1entry=hex(l1),l2_table_offset=l2off,l2index=l2index,l2entry=hex(entry),mapping_present=bool(entry&mask),captured_host_child_candidates=len(candidates))
    if candidates:
        last=candidates[-1];n=last['bytes'];at=last['child_file_offset'];raw=data[at:at+n]
        submit=[r for r in backend if r['phase']==4 and r['offset']==offset and r['bytes']==n][-1]
        row['last_first_range']=dict(**last,backend_id=submit['id'],captured_sha256=submit['sha256'],raw_image_sha256=hashlib.sha256(raw).hexdigest(),raw_image_equals_submitted=raw==submit['data'])
        if at+size<=len(data):
            body=data[at:at+size]
            row['raw_image_contiguous_file_sha256']=hashlib.sha256(body).hexdigest()
            if name=='payload2.txt':row['raw_image_contiguous_payload_exact']=body==bytes(33+(i*17+22)%90 for i in range(2226))
    rows.append(row)
commands={}
for cmd in re.findall(r'cmd 0x([0-9a-fA-F]+)',trace):commands[cmd]=commands.get(cmd,0)+1
result=dict(physical_access=False,cluster_size=cluster,files=rows,ide_command_counts=commands,
    observed_flush_cache_commands=commands.get('e7',0)+commands.get('ea',0),
    limits='Read-only closed-image mapping. Adjacent root/child request entries are checked against captured bytes and raw file bytes; mapping evidence alone does not establish guest normal shutdown or physical-console behavior.')
(out/'qcow-evidence.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
