# SPDX-License-Identifier: MIT
"""Independently inspect the actual516 object, ELF, sources, and final XBE."""
import hashlib,json,re,struct,subprocess,traceback
from datetime import datetime,timezone
from pathlib import Path
import candidate
from candidate import elf32,layout
K=Path(__file__).resolve().parent;P=Path('C:/xwn510/build001');O=Path('C:/xwn516/build001');R=Path('C:/xwn516/review001');OUT=K/'review001.json'
assert not R.exists() and not OUT.exists();R.mkdir()
sha=lambda b:hashlib.sha256(b).hexdigest();pins={}
def load(p):
    p=Path(p);b=p.read_bytes();pins[str(p)]=dict(bytes=len(b),sha256=sha(b));return b
def js(p):return json.loads(load(p))
def disk(n):return Path(n.replace('/mnt/c/','C:/',1))
def program_headers(b):
    off=elf32.u32(b,28);size,count=struct.unpack_from('<HH',b,42)
    assert size==32 and 0<count<=16 and off+size*count<=len(b)
    return [list(struct.unpack_from('<8I',b,off+i*size)) for i in range(count)]
def instructions(path):
    txt=subprocess.check_output(['wsl','-d','Ubuntu','--','objdump','-dw','-Mintel','--start-address=0x94877','--stop-address=0x94c18',path.as_posix().replace('C:/','/mnt/c/')],text=True,timeout=20)
    rows={}
    for line in txt.splitlines():
        m=re.match(r'\s*([0-9a-f]+):\s+((?:[0-9a-f]{2} )+)\s*([a-z][a-z0-9]*)\s*(.*)',line)
        if m:rows[int(m[1],16)]=(bytes.fromhex(m[2]),m[3],m[4])
    cur=layout.CODE
    for at,(b,_,_) in sorted(rows.items()):assert at==cur;cur+=len(b)
    assert cur==layout.END
    return txt,rows
r=dict(passed=False,started_utc=datetime.now(timezone.utc).isoformat(),physical_access=False,runtime_executed=False)
try:
    for n in ['review001.py','candidate.py']:load(K/n)
    for n in ['elf32.py','layout.py']:load(K.parent/'data-layout515'/n)
    build=js(K/'build001.json');prior=js(K.parent/'entry-trampoline510/build001.json');host=js(K/'host001.json')
    assert build['status']=='compiled' and host['passed']
    for rec in [build,prior]:
        for name,row in rec['files'].items():
            b=load(disk(name));assert len(b)==row['bytes'] and sha(b)==row['sha256'],name
    old=load(P/'default.xbe');actual=load(O/'default.xbe')
    assert len(actual)==len(old)==545088
    # Source-level change is only five exact owned namespace substitutions.
    sources=['xbeboot.S','xbe.S','font.S','witness.S','context.S','capture.S','entry.S','combined.S','indicator.S']
    for n in sources:assert load(O/n).replace(candidate.NEW_NAME,candidate.OLD_NAME)==load(P/n)
    oldobj=elf32.parse(load(P/'xbeboot.o'));newobj=elf32.parse(load(O/'xbeboot.o'))
    t=oldobj['named']['.text'];d=oldobj['named']['.data'];assert newobj['named']==oldobj['named']
    assert newobj['symbols']==oldobj['symbols'] and newobj['relocations']==oldobj['relocations']
    for name in ['.text','.data']:
        i=oldobj['named'][name]
        assert newobj['data'](newobj['sections'][i]).replace(candidate.NEW_NAME,candidate.OLD_NAME)==oldobj['data'](oldobj['sections'][i])
    oldsec,oldledger=elf32.relocated(oldobj,{t:layout.BASE,d:layout.OLD})
    newsec,newledger=elf32.relocated(newobj,{t:layout.BASE,d:layout.NEW})
    oldelf=elf32.parse(load(P/'wrapper.elf'));newelf=elf32.parse(load(O/'wrapper.elf'))
    for name,i in [('.text',t),('.data',d)]:
        assert oldsec[i]==oldelf['data'](oldelf['sections'][oldelf['named'][name]])
        assert newsec[i]==newelf['data'](newelf['sections'][newelf['named'][name]])
    # Derive namespace offsets directly from old and actual bytes, not builder flags.
    offsets=[];start=0
    while True:
        off=actual.find(candidate.NEW_NAME,start)
        if off<0:break
        offsets.append(off);start=off+len(candidate.NEW_NAME)
    assert len(offsets)==5 and offsets==host['namespace_offsets']
    assert actual.count(candidate.OLD_NAME)==1 and actual[layout.OLD-layout.BASE:]==old[layout.OLD-layout.BASE:]
    candidate.validate(actual,old,oldledger,t,d,offsets)
    assert sha(actual)==host['expected_sha256']==build['sha256']
    syold={x['name']:x['value'] for x in oldelf['symbols'] if x['name']}
    synew={x['name']:x['value'] for x in newelf['symbols'] if x['name']}
    assert set(syold)==set(synew)
    data_names={x['name'] for x in oldobj['symbols'] if x['section']==d and x['name']}
    moved=data_names|{'__bss_start','_edata','_end'}
    for n,v in syold.items():assert synew[n]==v+(layout.NEW-layout.OLD if n in moved else 0),n
    assert elf32.u32(actual,synew['Entry503Return']-layout.BASE)==syold['entry503_failed_file']
    assert synew['entry503_state']==0x94d10 and synew['entry498_record']==0x94c20
    # Warning is new and retained, not hidden or described as inherited.
    warning=load(O/'build.log').decode()
    assert warning=='/usr/bin/x86_64-linux-gnu-ld.bfd: warning: wrapper.elf has a LOAD segment with RWX permissions\n'
    oldph=program_headers(load(P/'wrapper.elf'));newph=program_headers(load(O/'wrapper.elf'))
    assert any(p[0]==1 and p[6]==7 for p in newph)
    assert elf32.u32(actual,0x348)==elf32.u32(old,0x348)==7
    # ELF is intermediate only. Final XBE section already had W/R/X flags7;
    # its entire header is identical except the existing section digest.
    assert actual[:0x36c]==old[:0x36c] and actual[0x380:4096]==old[0x380:4096]
    ot,oi=instructions(P/'wrapper.elf');nt,ni=instructions(O/'wrapper.elf')
    (R/'old-diagnostic.txt').write_bytes(ot.encode());(R/'new-diagnostic.txt').write_bytes(nt.encode())
    assert set(oi)==set(ni);edges=[];indirect=[];operand_changes=[]
    refs=[x for x in oldledger if x['section']==t and x['symbol_section']==d]
    assert len(refs)==72
    for at,(raw,mn,op) in oi.items():
        nraw,nmn,nop=ni[at];assert len(raw)==len(nraw) and mn==nmn
        assert raw==old[at-layout.BASE:at-layout.BASE+len(raw)] and nraw==actual[at-layout.BASE:at-layout.BASE+len(nraw)]
        rr=[x for x in refs if at<=x['address']<at+len(raw)]
        if rr:
            assert len(rr)==1;ref=rr[0]
            assert hex(ref['value']) in op and hex(ref['value']+layout.NEW-layout.OLD) in nop
            operand_changes.append(dict(address=at,old=op,new=nop))
        else:assert raw==nraw
        if mn.startswith('j') or mn.startswith('loop') or mn=='call':
            if op.startswith('DWORD PTR ds:'):
                a=int(op.split(':')[1],16);z=int(nop.split(':')[1],16)
                assert z==a+(layout.NEW-layout.OLD if layout.OLD<=a<layout.OLD+layout.SIZE else 0)
                indirect.append(dict(address=at,old_pointer=a,new_pointer=z))
            else:
                a=int(op.split()[0],16);z=int(nop.split()[0],16);assert a==z and a in oi;edges.append(dict(address=at,target=a))
    assert len(edges)==49 and len(operand_changes)==72
    rejected=0
    def reject(b):
        global rejected
        b[0x36c:0x380]=layout.digest(b)
        try:candidate.validate(bytes(b),old,oldledger,t,d,offsets)
        except ValueError:rejected+=1;return
        raise AssertionError('actual mutation accepted')
    for x in oldledger:
        if x['symbol_section']!=d:continue
        off=x['address']-layout.BASE if x['section']==t else layout.NEW-layout.BASE+x['offset']
        b=bytearray(actual);struct.pack_into('<I',b,off,x['value']);reject(b)
    for at in range(layout.NEW-layout.BASE,layout.NEW+layout.SIZE-layout.BASE):
        b=bytearray(actual);b[at]^=1;reject(b)
    for at in offsets:
        b=bytearray(actual);b[at:at+len(candidate.OLD_NAME)]=candidate.OLD_NAME;reject(b)
    (R/'actual-relocations.json').write_bytes((json.dumps(dict(old=oldledger,new=newledger,operand_changes=operand_changes,direct_edges=edges,indirect_edges=indirect),indent=2)+'\n').encode())
    r.update(passed=True,sha256=sha(actual),bytes=len(actual),relocations=len(oldledger),data_references=74,code_operand_changes=len(operand_changes),direct_edges_unchanged=len(edges),indirect_edges=indirect,source_reconstructions=len(sources),namespace_offsets=offsets,data_symbols_moved=len(data_names),generated_end_symbols_moved=3,all_other_symbols_unchanged=True,retained_old_tail_exact=True,full_header_except_digest_exact=True,whole_image_inverse_normalization_passed=True,actual_image_mutations_rejected=rejected,new_warning=warning,old_ELF_program_headers=oldph,new_ELF_program_headers=newph,warning_scope='Intermediate ELF co-locates code/data in RWX PT_LOAD; ELF is not deployed. Final XBE section flags remain original7, header permissions and extents byte-identical. Warning retained and explicitly reviewed; no suppression.',runtime_qualified=False)
except Exception:r['failure']=traceback.format_exc()
finally:
    r.update(finished_utc=datetime.now(timezone.utc).isoformat(),inputs=pins,private_files={str(p):dict(bytes=p.stat().st_size,sha256=sha(p.read_bytes())) for p in R.iterdir() if p.is_file()})
    OUT.write_bytes((json.dumps(r,indent=2)+'\n').encode());print(json.dumps({n:r[n] for n in ['passed','failure','sha256','actual_image_mutations_rejected'] if n in r}))
if not r['passed']:raise SystemExit(1)
