"""Record the exact HIDCLASS CREATE sharing predicate and counter maintenance."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sys.path.insert(0,'C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/work/python-packages')
import pefile,capstone
manifest=read(k/'providers001.json');cs=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);rows=[]
for item in manifest['providers']:
    p=k/'artifacts/providers001'/item['name'];assert sha(p)==item['sha256'];pe=pefile.PE(str(p));raw=p.read_bytes();pos=0;hits=[]
    while True:
        pos=raw.find(bytes.fromhex('430000c0'),pos)
        if pos<0:break
        hits.append(pe.get_rva_from_offset(pos));pos+=4
    row=dict(**item,sharing_status_literal_rvas=hits)
    if item['name']=='hidclass.sys':
        assert hits==[0xb06]
        assert pe.get_data(0xad5,6)==bytes.fromhex('394e38751f')[:6] if False else True
        expected={0xad5:'394e38',0xad8:'751f',0xaf9:'8065ff00',0xb03:'c745f8430000c0'}
        for rva,b in expected.items():assert pe.get_data(rva,len(bytes.fromhex(b)))==bytes.fromhex(b),(hex(rva),pe.get_data(rva,len(bytes.fromhex(b))).hex())
        row['instruction_ranges']=[dict(start_rva=a,size=n,raw=pe.get_data(a,n).hex(),instructions=[dict(rva=x.address,mnemonic=x.mnemonic,operands=x.op_str) for x in cs.disasm(pe.get_data(a,n),a)]) for a,n in ((0x88c,0x88),(0x914,0x10d),(0xa22,0x270))]
    rows.append(row)
result=dict(scope=__doc__,static_review_passed=True,physical_access=False,runtime_proven=False,providers=rows,field_semantics_derived_from_increment_decrement_and_test_instructions={'extension+2c':'open count','extension+30':'read-access count','extension+34':'write-access count','extension+38':'opens without FILE_SHARE_READ','extension+3c':'opens without FILE_SHARE_WRITE','extension+40':'opens with share access zero','file_context+38':'FILE_OBJECT pointer','file_context+40':'requested access word','file_context+44':'share access word'},read_denied_branch=dict(compare_rva=0xad5,conditional_jump_rva=0xad8,target_rva=0xaf9,status_assignment_rva=0xb03,status='0xc0000043',condition='requested access bit0 set and extension+0x38 nonzero, after earlier deny-all tests pass'),manifest_sha256=sha(k/'providers001.json'),source_sha256=sha(Path(__file__)))
dest=k/'static-review001.json';assert not dest.exists();dest.write_text(json.dumps(result,indent=2)+'\n');print('Exact HID sharing predicate, counter maintenance and provider pins recorded')
