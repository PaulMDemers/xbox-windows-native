"""Resolve captured return addresses against pinned images, instructions and kernel publics."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;repo=k.parents[2]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sys.path.insert(0,'C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/work/python-packages')
import pefile,capstone
t=read(k/'veto001/trace.json');plan=read(k/'preflight001.json')
assert t['status']=='both_class_failures_captured' and t['breakpoints_remaining']==0
pub=read(repo/'outputs/native-windows-nt5-kernel/kernel-publics.json')
assert pub['pdb_sha256']==read(k/'stack-layouts001.json')['pdb_sha256']
sy=sorted((v['rva'],n) for n,v in pub['symbols'].items())
cs=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
pes={n:pefile.PE(p['path']) for n,p in plan['providers'].items()}
for p in plan['providers'].values():assert sha(Path(p['path']))==p['sha256']
pins={(p['module'],p['rva']) for p in t['runtime_pins']}
def resolve(ref):
    row=dict(ref);name=ref.get('module')
    if name not in pes:return row
    rva=ref['rva'];pe=pes[name];assert (name,rva-16) in pins
    row['runtime_call_neighborhood_pinned']=True
    # A direct E8 immediately before the return is unambiguous when the
    # surrounding caller instruction stream independently reaches this boundary.
    row['ending_call_candidates']=[]
    for width in range(2,8):
        ins=list(cs.disasm(pe.get_data(rva-width,width),rva-width))
        if len(ins)==1 and ins[0].size==width and ins[0].mnemonic=='call':
            row['ending_call_candidates'].append(dict(rva=ins[0].address,bytes=ins[0].bytes.hex(),operands=ins[0].op_str))
    if name=='ntoskrnl.exe':
        start,symbol=next((p,n) for p,n in reversed(sy) if p<rva)
        row.update(nearest_public=symbol,public_rva=start,public_offset=rva-start)
        if rva-start<=0x10000:
            ins=list(cs.disasm(pe.get_data(start,rva-start),start))
            row['linear_decode_reaches_return']=bool(ins and ins[-1].address+ins[-1].size==rva)
            row['last_instructions']=[dict(rva=x.address,bytes=x.bytes.hex(),mnemonic=x.mnemonic,operands=x.op_str) for x in ins[-8:]]
    return row
rows=[]
for c in t['calls']:
    st=c['entry_stack'];assert 'read_error' not in st
    row=dict(id=c['id'],class_driver=c['caller']['module'],identity=c['identity'],enable=c['enable'],status=hex(c['status']),immediate_return=resolve(st['immediate_return']),frames=[dict(frame=f['frame'],previous=f['previous'],return_address=resolve(f['return_address']),words=f['words']) for f in st['frames']],termination=st['termination'])
    if c['status']==0xc0000043:
        rejection=next(e['rejection_stack'] for e in c['steps'] if e['site']=='hid_sharing_status')
        assert 'read_error' not in rejection
        row['rejection_frames']=[dict(frame=f['frame'],previous=f['previous'],return_address=resolve(f['return_address']),words=f['words']) for f in rejection['frames']]
    rows.append(row)
r=dict(scope=__doc__,review_passed=True,calls=rows,trace_sha256=sha(k/'veto001/trace.json'),script_sha256=sha(Path(__file__)),limits='Frame links and call-site pins are evidence; nearest-public names alone and raw stack words are not a complete unwind. FPO may omit intermediate routines. Functional input needs separate observation.')
dest=k/'stack-review001.json';assert not dest.exists();dest.write_text(json.dumps(r,indent=2)+'\n')
for c in rows:
    print(c['id'],c['class_driver'],c['status'],hex(c['immediate_return']['rva']))
    for f in c['frames']:
        a=f['return_address'];print(' ',a.get('module'),hex(a.get('rva',0)),a.get('nearest_public'),a.get('linear_decode_reaches_return'),a.get('ending_call_candidates'))
