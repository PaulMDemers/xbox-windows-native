"""Compile four path-literal changes; prove every other executable byte exact."""
import hashlib,json,os,shutil,struct,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('/mnt/c/xwn490/build001');O=Path('/mnt/c/xwn497/build002')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert os.environ.get('XWN_BUILD_LEASE')=='held' and not O.exists()
assert shutil.disk_usage('/mnt/c').free-32*1024**2>=20*1024**3
out=K/'build002.json';assert not out.exists()
prior=json.loads((K.parent/'context-adapter490/build001.json').read_text())
assert sha(P/'default.xbe')==prior['sha256']=='8cf6ec5457b02307cf7d9e6e8e29c629f960828da28ba43205a1b3e33ed5be78'
for n,v in prior['files'].items():assert sha(Path(n))==v['sha256'],n
O.mkdir(parents=True);changes=[]
for n in ['xbeboot.S','xbe.S','font.S','witness.S','context.S','capture.S']:
 b=(P/n).read_bytes();c=b.replace(b'Applications\\\\XWNBoot490a\\\\',b'Applications\\\\XWNBoot497a\\\\')
 assert c.replace(b'Applications\\\\XWNBoot497a\\\\',b'Applications\\\\XWNBoot490a\\\\')==b
 changes.append(dict(file=n,occurrences=b.count(b'Applications\\\\XWNBoot490a\\\\'),old_sha256=sha(P/n)))
 (O/n).write_bytes(c)
assert sum(v['occurrences'] for v in changes)==4
r=dict(status='building',diagnostic_schema=490,attempt=497,source_changes=changes,commands=[],physical_access=False)
def save():out.write_text(json.dumps(r,indent=2)+'\n')
save()
try:
 for cmd in prior['commands']:
  r['commands'].append(cmd)
  with (O/'build.log').open('ab') as f:subprocess.run(cmd,cwd=O,stdout=f,stderr=f,check=True,timeout=90)
 symbols=subprocess.check_output(['nm','-n','wrapper.elf'],cwd=O,text=True);(O/'symbols.txt').write_text(symbols)
 sym={v[2]:int(v[0],16) for line in symbols.splitlines() if len(v:=line.split())==3}
 assert sym==prior['wrapper_symbols']
 old=(P/'default.xbe').read_bytes();b=bytearray((O/'wrapper.bin').read_bytes())
 assert len(b)==len(old) and not any(b[0x3000:0x84000])
 b[:4096]=old[:4096];b[0x3000:0x84000]=old[0x3000:0x84000]
 b[0x36c:0x380]=hashlib.sha1(struct.pack('<I',len(b)-4096)+b[4096:]).digest()
 expected=bytearray(old);full=b'\\Device\\Harddisk0\\Partition1\\Applications\\XWNBoot490a\\'
 assert old.count(full)==4
 offsets=[]
 for suffix in [b'report.bin',b'refusal.bin',b'handoff.bin',b'context.bin']:
  literal=full+suffix+b'\0';assert old.count(literal)==1
  off=old.index(literal);new=literal.replace(b'XWNBoot490a',b'XWNBoot497a')
  expected[off:off+len(literal)]=new;offsets.append(dict(offset=off,bytes=len(literal),suffix=suffix.decode()))
 expected[0x36c:0x380]=hashlib.sha1(struct.pack('<I',len(expected)-4096)+expected[4096:]).digest()
 assert b==expected
 lo=sym['blentry']-0x10000;assert b[lo:lo+1024]==old[lo:lo+1024]
 lo=sym['capture490_begin']-0x10000;hi=sym['capture490_end']-0x10000
 assert hi-lo==313 and b[lo:hi]==old[lo:hi]
 (O/'default.xbe').write_bytes(b)
 r.update(status='compiled',sha256=sha(O/'default.xbe'),bytes=len(b),wrapper_symbols=sym,full_expected_binary_match=True,path_literals=offsets,changed_bytes=[dict(offset=i,before=a,after=z) for i,(a,z) in enumerate(zip(old,b)) if a!=z],payload_byte_exact=True,loader1024_byte_exact=True,capture313_byte_exact=True)
finally:
 r['files']={str(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in O.iterdir() if p.is_file()};save()
