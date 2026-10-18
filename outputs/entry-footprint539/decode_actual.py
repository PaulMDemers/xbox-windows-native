"""Decode a completed539 cold capture without claiming Windows execution."""
from pathlib import Path
import json,hashlib,struct,sys
K=Path(__file__).resolve().parent;sys.path.insert(0,str(K))
from primary_decode import decode as primary
from witness_decode import decode_witness
from decode import decode as context
from receipts import decode_refusal
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
assert len(sys.argv)==2 and sys.argv[1] in ('1',);i=int(sys.argv[1])
out=K/f'decoded{i}.json';assert not out.exists()
a=read(K/f'after{i}.json');assert a['completed'];files={}
for name,row in a['receipts'].items():
    if row is None:files[name]=None;continue
    b=Path(row['path']).read_bytes();assert hashlib.sha256(b).hexdigest()==row['sha256'];files[name]=b
r=dict(closed=True,ordinal=i,present={n:b is not None for n,b in files.items()},errors={},
       absence_proves_no_dispatch=False,windows_execution_proved=False,final_handoff_proved=False)
for name,action in [('report.bin',lambda:primary(files['report.bin'])),
                    ('refusal.bin',lambda:decode_refusal(files['refusal.bin']))]:
    if files[name] is not None:
        try:r[name]=action()
        except (ValueError,struct.error) as e:r['errors'][name]=str(e)
if files['report.bin'] is not None and files['handoff.bin'] is not None:
    try:r['handoff.bin']=decode_witness(files['handoff.bin'],files['report.bin'])
    except (ValueError,struct.error) as e:r['errors']['handoff.bin']=str(e)
if all(files[n] is not None for n in ['report.bin','handoff.bin','context.bin']) and not r['errors']:
    syms=read(K.parent/'context-adapter490/build001.json')['wrapper_symbols']
    try:
        frame=struct.unpack_from('<9I',files['handoff.bin'],160)
        r['context.bin']=context(files['context.bin'],witness_address=syms['witness_record'],
            frame_address=frame[3]-32,return_eips=[syms['context490_pre_return'],syms['context490_post_return']])
    except (ValueError,struct.error) as e:r['errors']['context.bin']=str(e)
r['source_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'ordinal':i,'present':r['present'],'errors':r['errors']}))
