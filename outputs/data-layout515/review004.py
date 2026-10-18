# SPDX-License-Identifier: MIT
"""One-shot retained-artifact review and in-memory layout negative controls."""
import hashlib,importlib.util,json,re,struct,subprocess,traceback
from datetime import datetime,timezone
from pathlib import Path
from elf32 import parse,relocated,u32
from layout import BASE,CODE,END,OLD,SIZE,NEW,proposal,validate,digest,check_base

K=Path(__file__).resolve().parent;P=K.parent
O=Path('C:/xwn510/build001');R=Path('C:/xwn515/review004');OUT=K/'review004.json'
assert not OUT.exists() and not R.exists();R.mkdir()
sha=lambda b:hashlib.sha256(b).hexdigest()
pins={}
def load(path):
    path=Path(path);b=path.read_bytes();pins[str(path)]=dict(bytes=len(b),sha256=sha(b));return b
def js(path):return json.loads(load(path))
def mapped(path):return Path(path.replace('/mnt/c/','C:/',1))
def verify_files(record):
    for name,row in record['files'].items():
        b=load(mapped(name));assert len(b)==row['bytes'] and sha(b)==row['sha256'],name
def write(path,obj):path.write_bytes((json.dumps(obj,indent=2)+'\n').encode())
def disassemble(path,raw=False):
    cmd=['wsl','-d','Ubuntu','--','objdump',('-Dw' if raw else '-dw'),'-Mintel']
    if raw:cmd+=['-b','binary','-m','i386','--adjust-vma='+hex(CODE)]
    else:cmd+=['--start-address='+hex(CODE),'--stop-address='+hex(END)]
    cmd+=[path.as_posix().replace('C:/','/mnt/c/')]
    text=subprocess.check_output(cmd,text=True,timeout=20)
    result={}
    for line in text.splitlines():
        m=re.match(r'\s*([0-9a-f]+):\s+((?:[0-9a-f]{2} )+)\s*([a-z][a-z0-9]*)\s*(.*)',line)
        if m:result[int(m[1],16)]=(bytes.fromhex(m[2]),m[3],m[4])
    cursor=CODE
    for address,(b,_,_) in sorted(result.items()):assert address==cursor;cursor+=len(b)
    assert cursor==END
    return text,result

r=dict(passed=False,started_utc=datetime.now(timezone.utc).isoformat(),scope='HOST-ONLY static retained-artifact review; synthetic in-memory relocation, no candidate build or launch',physical_access=False)
try:
    for name in ['elf32.py','layout.py','review004.py']:load(K/name)
    build=js(P/'entry-trampoline510/build001.json');verify_files(build)
    assert build['sha256']=='fe9d78fa2f07d4804d0a82a66188e45293ac45a212575613369815c766c7f83f'
    b=load(O/'default.xbe');e=parse(load(O/'xbeboot.o'));linked=parse(load(O/'wrapper.elf'))
    t=e['named']['.text'];d=e['named']['.data']
    old,ledger=relocated(e,{t:BASE,d:OLD});new,newledger=relocated(e,{t:BASE,d:NEW})
    for name,index in [('.text',t),('.data',d)]:
        assert old[index]==linked['data'](linked['sections'][linked['named'][name]])
    assert len(ledger)==395 and len(old[t])==END-BASE and len(old[d])==SIZE
    assert not any(b[END-BASE:OLD-BASE])
    datarefs=[x for x in ledger if x['symbol_section']==d]
    assert len(datarefs)==74 and all(x['kind']==1 for x in datarefs)
    coderefs=[x for x in datarefs if x['section']==t]
    assert len(coderefs)==72 and all(CODE<=x['address']<END-3 for x in coderefs)
    # An independent byte scan of the exact diagnostic has no unmatched pointer
    # into the old data interval. This is bounded static coverage, not dynamic taint.
    scan={a for a in range(CODE,END-3) if OLD<=u32(b,a-BASE)<OLD+SIZE}
    assert scan=={x['address'] for x in coderefs}
    assert all(a['value']==z['value'] for a,z in zip(ledger,newledger) if a['symbol_section']!=d)
    synthetic=proposal(b,old,new,t,d);validate(synthetic,b,ledger,t,d)
    assert synthetic[0x1100:0x1105]==b[0x1100:0x1105] and synthetic[OLD-BASE:]==b[OLD-BASE:]
    assert not any(OLD<=u32(synthetic,a-BASE)<OLD+SIZE for a in range(CODE,END-3))
    # Only the independently authored diagnostic fragment is written, never the
    # payload-bearing proposed XBE. This file cannot be launched as an XBE.
    fragment=R/'proposed-diagnostic.bin';fragment.write_bytes(synthetic[CODE-BASE:END-BASE])
    ot,oi=disassemble(O/'wrapper.elf');nt,ni=disassemble(fragment,True)
    (R/'original-diagnostic.txt').write_bytes(ot.encode());(R/'proposed-diagnostic.txt').write_bytes(nt.encode())
    assert set(oi)==set(ni)
    operand_rows=[];direct=[];indirect=[]
    for address,(raw,mnemonic,operand) in oi.items():
        nraw,nmnemonic,noperand=ni[address];assert mnemonic==nmnemonic and len(raw)==len(nraw)
        assert raw==b[address-BASE:address-BASE+len(raw)]
        assert nraw==synthetic[address-BASE:address-BASE+len(nraw)]
        refs=[x for x in coderefs if address<=x['address']<address+len(raw)]
        if refs:
            assert len(refs)==1
            x=refs[0];assert x['address']+4<=address+len(raw)
            assert hex(x['value']) in operand and hex(x['value']+NEW-OLD) in noperand
            operand_rows.append(dict(address=address,mnemonic=mnemonic,old=operand,new=noperand))
        else:assert raw==nraw
        if mnemonic.startswith('j') or mnemonic.startswith('loop') or mnemonic=='call':
            if operand.startswith('DWORD PTR ds:'):
                oldptr=int(operand.split(':')[1],16);newptr=int(noperand.split(':')[1],16)
                assert newptr==oldptr+(NEW-OLD if OLD<=oldptr<OLD+SIZE else 0)
                indirect.append(dict(address=address,old_pointer=oldptr,new_pointer=newptr))
            else:
                oldto=int(operand.split()[0],16);newto=int(noperand.split()[0],16)
                assert oldto==newto and oldto in oi
                direct.append(dict(address=address,target=oldto))
    assert len(operand_rows)==72 and len(direct)==49
    first=[dict(address=a,mnemonic=oi[a][1],operand=oi[a][2]) for a in sorted(oi) if 0x94aff<=a<0x94b20]
    assert oi[0x94aff][1]=='pushf' and oi[0x94b00][1]=='pusha' and oi[0x94b01][1]=='cld'
    assert oi[0x94b02][1]=='cmp' and '0x950f0' in oi[0x94b02][2]
    assert ni[0x94b02][1]=='cmp' and hex(NEW+0xf0) in ni[0x94b02][2]
    # Meaningful negatives: each omitted/stale relocation, wrong base/extent,
    # changes to the preserved tail, operands/opcodes/imports and metadata.
    rejected=[]
    def refuse(candidate,label):
        try:validate(candidate,b,ledger,t,d)
        except ValueError:rejected.append(label);return
        raise AssertionError('accepted mutation '+label)
    for i,x in enumerate(datarefs):
        bad=bytearray(synthetic)
        off=x['address']-BASE if x['section']==t else NEW-BASE+x['offset']
        struct.pack_into('<I',bad,off,x['value']);bad[0x36c:0x380]=digest(bad)
        refuse(bytes(bad),'stale-pointer-'+str(i))
    # Byte negatives cover the entire diagnostic/data, retained tail, headers,
    # unused gap, imports and trampoline; digests are repaired to avoid triviality.
    positions=set(range(CODE-BASE,END-BASE))|set(range(NEW-BASE,NEW+SIZE-BASE))|set(range(OLD-BASE,len(b)))
    positions.update(range(0x1000,0x102c));positions.update(range(0x1100,0x1107))
    positions.update(range(0,0x36c));positions.update(range(0x380,4096))
    positions.update(range(END-BASE,NEW-BASE));positions.update(range(NEW+SIZE-BASE,OLD-BASE,16))
    for off in sorted(positions):
        bad=bytearray(synthetic);bad[off]^=1;bad[0x36c:0x380]=digest(bad)
        refuse(bytes(bad),'byte-'+hex(off))
    refuse(synthetic[:-1],'short');refuse(synthetic+b'\0','long')
    refused_bases=[]
    for value in [True,-16,0,0x94c10,0x94c18,0x94c21,0x94ed0,0x94f00,0x95000,0xfffffff0]:
        try:check_base(value)
        except ValueError:refused_bases.append(value);continue
        raise AssertionError('accepted invalid base '+hex(value))
    # Compare old physical evidence by exact retained bytes and the original
    # independent decoder. This is offline reanalysis, not a new collection.
    b494=js(P/'d3d-transform494/build002.json');s494=b494['wrapper_symbols']
    elf494=parse(load('C:/xwn494/build002/wrapper.elf'))
    sym494={x['name']:x['value'] for x in elf494['symbols'] if x['name']}
    for name in ['context490_packet','context490_first','context490_second','context490_pre_return','context490_post_return','capture490_begin','capture490_end']:
        assert s494[name]==sym494[name]
    assert s494['context490_packet']==0x94558 and s494['capture490_begin']==0x9473e and s494['capture490_end']==CODE
    c494=js(P/'d3d-transform494/physical001-collection.json');assert c494['completed'] and c494['hook_removed']
    def receipt(name):
        row=c494['files']['/E/Applications/XWNBoot494a/'+name];data=load(row['path'])
        assert len(data)==row['bytes'] and sha(data)==row['sha256'];return data
    ctx=receipt('context.bin');wit=receipt('handoff.bin');frame=struct.unpack_from('<9I',wit,160)
    decoder=P/'d3d-transform494/decode.py';load(decoder);load(P/'cpu-context489/decode.py')
    spec=importlib.util.spec_from_file_location('old494_context',decoder);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    decoded=module.decode(ctx,witness_address=s494['witness_record'],frame_address=frame[3]-32,return_eips=[s494['context490_pre_return'],s494['context490_post_return']])
    prior=js(P/'d3d-transform494/actual-context001.json');assert decoded==prior['context'] and prior['passed']
    emu=js(P/'entry-contract513/actual-review001.json');physical=js(P/'entry-physical514/physical-final001.json')
    assert emu['passed'] and emu['mappings']['data']['virtual']==OLD
    assert physical['closed'] and physical['entry']['entry_state']=='absent_in_listing' and not physical['entry']['absence_proves_no_entry']
    write(R/'relocations.json',dict(original=ledger,proposed=newledger,operand_inventory=operand_rows,direct_edges=direct,indirect_edges=indirect))
    r.update(passed=True,retained_linked_sections_reconstructed=['.text','.data'],relocations=len(ledger),data_references=len(datarefs),code_data_references=len(coderefs),data_internal_references=len(datarefs)-len(coderefs),direct_edges_unchanged=len(direct),indirect_edges=indirect,first_instructions=first,
        original_data=[OLD,OLD+SIZE],proposed_data=[NEW,NEW+SIZE],zero_gap=[END,OLD],old_data_tail_preserved=True,image_extents_imports_entry_unchanged=True,
        synthetic_image_sha256=sha(synthetic),synthetic_image_saved=False,negative_byte_and_pointer_controls=len(rejected),invalid_bases_rejected=refused_bases,
        physical494=dict(context_sha256=sha(ctx),decoded=decoded,packet_address=s494['context490_packet'],capture_code=[s494['capture490_begin'],s494['capture490_end']],current_mapping_proof=False),
        emulator513_data_mapping=emu['mappings']['data'],physical514_receipt_absent=True,physical514_entry_execution_unknown=True,cause_established=False,
        limitations=['Static references and synthetic relocation only; no new instructions executed.','494 historical 0x94000 access does not prove current mapping or exact 0x94c20 access.','513 mapping is emulator evidence only.','No new namespace or actual candidate build; full exact-candidate observer and host sequencing tests remain required.'])
except Exception:
    r['failure']=traceback.format_exc()
finally:
    r['finished_utc']=datetime.now(timezone.utc).isoformat();r['inputs']=pins
    r['private_files']={str(p):dict(bytes=p.stat().st_size,sha256=sha(p.read_bytes())) for p in R.iterdir() if p.is_file()}
    write(OUT,r);print(json.dumps({k:r[k] for k in ['passed','failure','relocations','data_references','negative_byte_and_pointer_controls'] if k in r}))
if not r['passed']:raise SystemExit(1)
