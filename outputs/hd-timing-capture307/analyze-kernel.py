"""Read-only analysis of actual privately captured retail kernel; no proprietary bytes committed."""
import hashlib,json,struct,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;r=json.loads((k/'physical001/trial.json').read_text());assert r['collected'] and r['independent_log_review']['passed']
row=r['private_kernel'];p=Path(row['path']);data=p.read_bytes();sha=lambda b:hashlib.sha256(b).hexdigest();assert sha(data)==row['sha256']
q=r['independent_log_review']['kernel'];base=int(q['base'],16)
u=lambda o:struct.unpack_from('<I',data,o)[0];h=lambda o:struct.unpack_from('<H',data,o)[0]
pe=u(0x3c);assert data[pe:pe+4]==b'PE\0\0';n=h(pe+6);opt=pe+24;assert h(opt)==0x10b and 1<=n<=32
assert u(opt+28)==base and u(opt+56)==len(data)
headers=u(opt+60);assert 0<headers<=4096
image=bytearray(data[:headers]);sections=[]
for i in range(n):
 at=opt+h(pe+20)+40*i;name=data[at:at+8].split(b'\0')[0].decode('ascii');vsize,rva,rawsize,raw=struct.unpack_from('<4I',data,at+8)
 assert rva+rawsize<=len(data) and raw+rawsize<8*1024**2
 if len(image)<raw+rawsize:image.extend(bytes(raw+rawsize-len(image)))
 image[raw:raw+rawsize]=data[rva:rva+rawsize]
 sections.append(dict(name=name,virtual_address=base+rva,virtual_size=vsize,raw_size=rawsize,flags=u(at+36),sha256=sha(data[rva:rva+rawsize])))
private=p.parent/'analysis001';assert not private.exists();private.mkdir();exe=private/'kernel-reconstructed.exe';exe.write_bytes(image)
proc=subprocess.run(['C:/msys64/mingw64/bin/llvm-objdump.exe','-d','--x86-asm-syntax=intel',str(exe)],capture_output=True,timeout=60,check=True);(private/'disassembly.txt').write_bytes(proc.stdout)
export=u(opt+96);count=u(export+20);ordinal_base=u(export+16);functions=u(export+28);assert count<512
exports={str(ordinal_base+i):base+u(functions+4*i) for i in range(count)}
for ordinal,name in [('2','avoption'),('3','avset'),('45','smbread'),('50','smbwrite')]:
 # Record actual export identities; an unfamiliar ordinal refuses instead of guessed substitution.
 assert exports[ordinal]==int(q[name],16),(ordinal,name,hex(exports[ordinal]),q[name])
report=dict(captured_kernel_sha256=sha(data),base=base,image_size=len(data),timestamp=u(pe+8),sections=sections,exports=exports,actual_kernel_version='1.0.4034.1',missing_pages=r['independent_log_review']['kernel_page_validity'].count(0),private_derived={str(x):dict(bytes=x.stat().st_size,sha256=sha(x.read_bytes())) for x in private.iterdir()},scope='Loaded retail kernel image and exports; static disassembly only, no runtime SMBus write trace',encoder_protocol_established=False)
p=k/'kernel-review001.json';assert not p.exists();p.write_text(json.dumps(report,indent=2)+'\n');print({a:report[a] for a in ['base','image_size','timestamp','missing_pages','encoder_protocol_established']})
