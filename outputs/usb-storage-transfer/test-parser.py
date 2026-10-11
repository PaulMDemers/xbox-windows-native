"""Exercise correlation failures, pointer reuse and malformed binary framing."""
import importlib.util,json,tempfile
from pathlib import Path
k=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('transfer',k/'parse-transfer.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def row(seq,ident,phase,t,owner=100,offset=8004132864,size=512,data=b'Q'*512,flags=0,qiov=200,status=0):
    return dict(sequence=seq,id=ident,phase=phase,monotonic_us=t,owner=owner,
        offset=offset,bytes=size,data=data,payload_bytes=len(data),flags=flags,
        qiov=qiov,qiov_offset=0,status=status,sha256='synthetic')
dma=[];back=[]
for ident,start in [(1,0),(2,10)]:
    dma.extend([row(len(dma)+1,ident,0,start,data=b'',flags=1),
        row(len(dma)+2,ident,11,start,offset=4096,data=b''),
        row(len(dma)+3,ident,1,start+1),row(len(dma)+4,ident,2,start+4),
        row(len(dma)+5,ident,3,start+5,offset=8004133376,size=0,data=b'')])
    back.extend([row(len(back)+1,ident,4,start+2,owner=300),
                 row(len(back)+2,ident,5,start+3,owner=300)])
a=m.analyze(dma,back)
assert a['matched_chunks']==2 and not a['issues'] and not a['outstanding_dma']
assert all(c['all_four_bytes_equal'] for c in a['chunks'])
back[3]=dict(back[3],data=b'R'*512)
assert m.analyze(dma,back)['chunks'][1]['all_four_bytes_equal'] is False
back[3]=dict(back[3],status=-5)
assert m.analyze(dma,back)['chunks'][1]['backend_status']==-5
partial=m.analyze(dma[:-1],back)
assert partial['outstanding_dma']==[2] and partial['issues']
bad=list(back);bad[3]=dict(bad[3],qiov=201)
try:m.analyze(dma,bad)
except AssertionError:pass
else:raise AssertionError('Mismatched identity accepted')
header=m.HEADER.pack(m.MAGIC,1,1,1,1,8004132864,512,200,100,0,1,0,512,0,1,0)
with tempfile.TemporaryDirectory(prefix='transfer-parser-') as directory:
    path=Path(directory)/'synthetic.bin';path.write_bytes(header+b'Q'*512)
    assert m.records(path)[0]['data']==b'Q'*512
    for data in [header[:-1],header+b'Q'*511,b'\0'*128]:
        path.write_bytes(data)
        try:m.records(path)
        except AssertionError:pass
        else:raise AssertionError('Malformed framing accepted')
result=dict(reused_pointer_generations=True,changed_completion_bytes_detected=True,
    negative_backend_status_retained=True,incomplete_lifecycle_retained=True,
    mismatched_identity_rejected=True,truncated_header_rejected=True,
    truncated_payload_rejected=True,invalid_magic_rejected=True)
(k/'parser-validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
