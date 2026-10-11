"""Pin registration/button-policy instructions and the built emulator's HID descriptors."""
import ast,hashlib,json,re,sys
from pathlib import Path
k=Path(__file__).resolve().parent;repo=k.parents[2]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sys.path.insert(0,'C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/work/python-packages')
import pefile,capstone
p=k.parent/'artifacts/providers001/ntoskrnl.exe';assert sha(p)=='84172dbd7e148dcf6e87c2e75e0c8716b3afcb6041b39802f63fd7fb67d7a152'
pe=pefile.PE(str(p));cs=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
sites=ast.literal_eval(next(line.split('=',1)[1] for line in (k/'preflight.py').read_text().splitlines() if line.startswith('policy_sites=')))
ranges=[]
for start,end in ((0x15ad00,0x15ad25),(0xa381a,0xa388e),(0x210fc,0x215a0),(0xdd976,0xddbda),(0xde13e,0xde2ce)):
    raw=pe.get_data(start,end-start);ranges.append(dict(start_rva=start,raw=raw.hex(),instructions=[dict(rva=x.address,mnemonic=x.mnemonic,operands=x.op_str,bytes=x.bytes.hex()) for x in cs.disasm(raw,start)]))
assert pe.get_data(0xde214,5)==bytes.fromhex('b940412900')
assert pe.get_data(0xde1f5,5)==bytes.fromhex('b944412900')
assert pe.get_data(0xde2c1,5)==bytes.fromhex('e82efbf3ff')
manifest=read(k/'emulator-source001.json')
for row in manifest['files']:assert sha(k/row['snapshot'])==row['sha256']
source=(k/'artifacts/emulator-source001/hw_usb_dev-hid.c').read_text();descriptors=[]
for device in ('mouse','keyboard'):
    name='qemu_'+device+'_hid_report_descriptor';body=source.split(name+'[] = {',1)[1].split('};',1)[0]
    body=re.sub(r'/\*.*?\*/','',body,flags=re.S);raw=bytes(int(v,16) for v in re.findall(r'0x([0-9a-fA-F]+)',body))
    offset=0;page=0;usages=[];collections=[];items=[]
    while offset<len(raw):
        prefix=raw[offset];assert prefix!=0xfe;n=(0,1,2,4)[prefix&3];typ=(prefix>>2)&3;tag=prefix>>4;value=int.from_bytes(raw[offset+1:offset+1+n],'little')
        assert offset+1+n<=len(raw);items.append(dict(offset=offset,prefix=prefix,value=value,usage_page=page))
        if typ==1 and tag==0:page=value
        if typ==2 and tag==0:usages.append(value)
        if typ==0:
            if tag==10:collections.append(dict(kind=value,usage_page=page,usages=list(usages)))
            usages=[]
        offset+=1+n
    assert [(x['usage_page'],x['usages']) for x in collections if x['kind']==1]==[(1,[2 if device=='mouse' else 6])]
    assert not any(x['usage_page']==1 and 0x80 in x['usages'] for x in collections)
    descriptors.append(dict(device=device,source_symbol=name,raw=raw.hex(),sha256=hashlib.sha256(raw).hexdigest(),collections=collections,items=items,generic_desktop_system_control_collection=False))
result=dict(static_review_passed=True,kernel_sha256=sha(p),sites={n:dict(rva=a,raw=pe.get_data(a,16).hex()) for n,a in sites.items()},instruction_ranges=ranges,emulator_descriptors=descriptors,emulator_source_manifest_sha256=sha(k/'emulator-source001.json'),script_sha256=sha(Path(__file__)),ioctl_names={'0x294140':'IOCTL_GET_SYS_BUTTON_CAPS','0x294144':'IOCTL_GET_SYS_BUTTON_EVENT'},definition_source='https://raw.githubusercontent.com/microsoft/win32metadata/main/generation/WinSDK/RecompiledIdlHeaders/shared/poclass.h',limits='Current Microsoft header supplies names/constants only; exact NT5 image supplies behavior. Built USB mouse/keyboard descriptors lack Generic Desktop System Control collections. This does not qualify console SMC power, host power events or a physical button. Runtime capability query outcomes must be observed separately.')
dest=k/'policy-static001.json';assert not dest.exists();dest.write_text(json.dumps(result,indent=2)+'\n');print('Kernel sites and exact built USB descriptors pinned; runtime results still required')
