"""Match the captured hard-error caller to the owned win32k image and imports."""
import hashlib
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parent
sys.path.insert(0, str(root.parents[1] / 'work/python-packages'))
import capstone
import pefile

binary = Path('E:/Codex-archive/xbox-windows-native/0.1.0/physical-files/F/winnt/system32/win32k.sys')
pe = pefile.PE(str(binary))
runtime = json.loads((root/'001/runtime.json').read_text())
module = next(m for m in runtime['modules'] if m['name'].lower() == 'win32k.sys')
base = int(module['base'],16)
assert base == pe.OPTIONAL_HEADER.ImageBase == 0xa0000000
assert module['size'] == (pe.OPTIONAL_HEADER.SizeOfImage+4095)&~4095
trace = json.loads((root/'001/trace.json').read_text())
event = trace['events'][0]
assert event['function'] == '_ExRaiseHardError@24'
assert event['caller'] == '0xa007e406' and event['arguments'][0] == '0xc000026b'
imports = {item.address:item.name.decode() for dll in pe.DIRECTORY_ENTRY_IMPORT
           for item in dll.imports if item.name}
assert imports[0xa016490c] == 'ExRaiseHardError'
assert imports[0xa0164908] == 'ZwTerminateProcess'
assert pe.get_data(0x7e400,6).hex() == 'ff150c4916a0'
md = capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
instructions = list(md.disasm(pe.get_data(0x7e103,0x7e419-0x7e103),base+0x7e103))
assert any(i.address==0xa007e400 and i.mnemonic=='call' and i.size==6 for i in instructions)
review = dict(
    scope=__doc__, binaries={'win32k.sys':dict(sha256=hashlib.sha256(binary.read_bytes()).hexdigest(),preferred_base=hex(base))},
    runtime_module=module, pe_size_of_image=pe.OPTIONAL_HEADER.SizeOfImage,
    module_size_matches_page_rounded_image=True, trace_event=0, caller=event['caller'],
    import_targets={hex(a):imports[a] for a in [0xa0164908,0xa016490c]},
    instructions=[dict(address=hex(i.address),bytes=i.bytes.hex(),instruction=i.mnemonic+' '+i.op_str)
                  for i in instructions if i.address>=0xa007e386],
    conclusion='Captured return address follows the matched win32k call to ExRaiseHardError with constant0xc000026b. The following code requests termination of the current process using0xc0000142.',
    limits='The subsequent termination is static control-flow evidence, not a separately captured call. No private function name or physical device identity is inferred; cold binary matching is required separately.')
(root/'caller-review.json').write_text(json.dumps(review,indent=2)+'\n')
print('Matched win32k caller and hard-error import; cold identity check still required.')
