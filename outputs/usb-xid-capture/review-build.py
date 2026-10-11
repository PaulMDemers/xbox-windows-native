"""Check frozen inputs and that both USB fixes actually won the native link."""
import hashlib,json,re,struct,sys
from pathlib import Path
k=Path(__file__).resolve().parent;attempt=sys.argv[1];r=json.loads((k/(attempt+'-inputs.json')).read_text());folder=Path(r['build_folder'])
sha=lambda b:hashlib.sha256(b).hexdigest()
for name,digest in r['pins'].items():assert sha(Path(name).read_bytes())==digest,name
assert sha((folder/'usb_core_guarded.c').read_text().encode())==r['guarded_core_sha256']
assert sha((folder/'ohci_guarded.c').read_text().encode())==r['guarded_ohci_sha256']
assert (folder/'main.c').read_bytes()==(k/'main.c').read_bytes()
link=(folder/'link.map').read_text();ownership={}
for symbol,obj in [('usbh_ctrl_xfer','usb_core_guarded.obj'),('usbh_int_xfer','usb_core_guarded.obj'),('ohci_driver','ohci_guarded.obj'),('xid_guard_reboot','main.obj')]:
 rows=[line for line in link.splitlines() if re.search(r'\b_'+symbol+r'\s',line)]
 assert len(rows)==1 and rows[0].strip().endswith(obj),(symbol,rows)
 ownership[symbol]=obj
pe=(folder/'main.exe').read_bytes();offset=struct.unpack_from('<I',pe,0x3c)[0]
assert pe[offset:offset+4]==b'PE\0\0' and struct.unpack_from('<H',pe,offset+4)[0]==0x14c
xbe=(folder/'bin/default.xbe').read_bytes();assert xbe[:4]==b'XBEH'
assert '$(CURDIR)/main.obj: CFLAGS += -Werror' in (folder/'Makefile').read_text()
review=dict(passed=True,attempt=attempt,emulator=r['emulator'],xbe_sha256=sha(xbe),main_sha256=sha((folder/'main.c').read_bytes()),link_ownership=ownership,shared_sdk_inputs_unchanged=True,physical_access=False,upstream_warnings=['unused hdr','signed/unsigned comparisons','unused t0 and i'],runtime_qualified=False)
(k/(attempt+'-review.json')).write_text(json.dumps(review,indent=2)+'\n');print(json.dumps(review))
