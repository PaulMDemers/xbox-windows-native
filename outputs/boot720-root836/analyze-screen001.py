"""Pin user BSOD photograph and resolve fault against installed-image manifest."""
import datetime,hashlib,json,sys,zipfile
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn836')
sys.path.insert(0,str(W/'work/python-packages'))
import pefile,capstone
sha=lambda b:hashlib.sha256(b).hexdigest();read=lambda p:json.loads(p.read_text())
out=K/'screen001.json';assert not out.exists()
photo=Path('C:/Users/Paul/.codex/codex-remote-attachments/01a0ff98-aa67-78c0-baa4-279c9bacf1d2/25FB1404-5C6B-4FFD-9AB5-BB4FAA9753DE/1-Photo-1.jpg').read_bytes()
assert not (P/'screen001.jpg').exists();(P/'screen001.jpg').write_bytes(photo)
r={'utc_recorded':datetime.datetime.now(datetime.timezone.utc).isoformat(),'photo_sha256':sha(photo),'photo_bytes':len(photo),
 'stop':'0x0000000A','name':'IRQL_NOT_LESS_OR_EQUAL','parameters':['0x00000018','0x00000002','0x00000000','0x8244F167'],
 'displayed_module':'ntoskrnl.exe','displayed_base':'0x82409000','displayed_timestamp':'0x4b7a1bd5',
 'windows_kernel_entry_observed':True,'windows_desktop_observed':False,
 'console_state':'Held Windows blue screen; power off/on requested, dashboard authentication pending',
 'limitations':'Photo supplies no call stack, register dump or corrupting writer. Display is readable; resolution inferred from retained720p boot contract, not measured from photo.'}
out.write_text(json.dumps(r,indent=2)+'\n')
pkg=read(W/'outputs/boot720-native835/package001.json');v=pkg['files']['/E/winnt/system32/ntoskrnl.exe']
archive=Path('E:/xwn343/bundle002/stock-e-1080i-001.zip');assert sha(archive.read_bytes())==pkg['archive_sha256']
with zipfile.ZipFile(archive) as z:data=z.read('payload'+v['archive_path'])
assert len(data)==v['bytes'] and sha(data)==v['sha256'];(P/'analysis001').mkdir();(P/'analysis001/ntoskrnl.exe').write_bytes(data)
pe=pefile.PE(data=data);assert pe.FILE_HEADER.TimeDateStamp==0x4b7a1bd5
pub=read(W/'outputs/native-windows-nt5-kernel/kernel-publics.json')
assert sha((W/'work/symbols/ntoskrnl-2195-7376.pdb').read_bytes())==pub['pdb_sha256']
base=0x82409000;pc=0x8244f167;rva=pc-base
syms=sorted((v['rva'],n) for n,v in pub['symbols'].items())
start,name=max((a,n) for a,n in syms if a<=rva)
cs=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
ins=list(cs.disasm(pe.get_data(start,rva-start+48),start))
fault=next(i for i in ins if i.address==rva)
analysis={'kernel_sha256':sha(data),'pdb_sha256':pub['pdb_sha256'],'rva':hex(rva),'nearest_symbol':name,'symbol_offset':hex(rva-start),
 'fault_instruction':{'rva':hex(fault.address),'mnemonic':fault.mnemonic,'operands':fault.op_str},
 'instructions':[{'rva':hex(i.address),'mnemonic':i.mnemonic,'operands':i.op_str} for i in ins if rva-64<=i.address<=rva+32],
 'interpretation':'Bugcheck reports a read of address0x18 at IRQL2. Root cause and call stack remain unknown.',
 'kernel_source':'Immutable installation archive; post-boot physical readback still pending'}
(K/'fault-analysis001.json').write_text(json.dumps(analysis,indent=2)+'\n')
note='''# Boot836 reached Windows kernel; STOP0A at ntoskrnl+46167

User photo screen001.json: IRQL_NOT_LESS_OR_EQUAL, arguments18,2,0,8244F167,
kernel base82409000 timestamp4b7a1bd5. Readable Windows blue screen, not desktop.
FATX root fix passed the previous SYSTEM.ALT boundary. Do not infer root cause
from the fault address alone. See fault-analysis001.json for pinned symbol mapping.

836 remains OPEN pending return/collection. User asked to power off/on and leave
UnleashX. Independently authenticate dashboard, no hook to remove, collect836 once,
audit installed files and boot traces. No relaunch. No owned host runtime.
Next diagnose Windows kernel failure with fixed720p retained; no mode probes.
835 CLOSED. Old automation paused, direct Windows desktop work authorized.

'''
(K/'NEXT.md').write_text(note)
for p in [W/'outputs/engineering-notes/CONTINUATION.md',W/'outputs/engineering-notes/STATUS.md',W/'docs/current-status.md']:p.write_bytes(note.encode()+p.read_bytes())
print(json.dumps(analysis,indent=2))
