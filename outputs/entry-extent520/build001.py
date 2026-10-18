# SPDX-License-Identifier: MIT
"""Privately rebuild exact516 sources with namespace only, then reviewed extent."""
import datetime,hashlib,json,os,shutil,struct,subprocess,traceback
from pathlib import Path
import candidate
from candidate import extent
K=Path(__file__).resolve().parent;P=Path('/mnt/c/xwn516/build001');O=Path('/mnt/c/xwn520/build001');OUT=K/'build001.json'
assert os.environ.get('XWN_BUILD_LEASE')=='held' and not O.exists() and not OUT.exists()
assert shutil.disk_usage('/mnt/c').free-32*1024**2>=20*1024**3
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();js=lambda p:json.loads(p.read_bytes())
utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def mapped(n):return Path(n.replace('C:\\','/mnt/c/').replace('C:/','/mnt/c/').replace('\\','/'))
host=js(K/'host001.json');prior=js(K.parent/'entry-colocated516/build001.json')
assert host['passed'] and host['closed'] and prior['status']=='compiled'
for n,h in host['inputs'].items():assert sha(mapped(n))==h,n
for n,row in prior['files'].items():assert sha(Path(n))==row['sha256'],n
sources=['xbeboot.S','xbe.S','font.S','witness.S','context.S','capture.S','entry.S','combined.S','indicator.S']
tools=[Path('/usr/bin')/n for n in ['x86_64-linux-gnu-gcc-12','as','ld','objcopy','objdump','nm']]
for p in tools:assert sha(p)==prior['inputs'][str(p)],p
parent=(P/'default.xbe').read_bytes();expected=candidate.prepare(parent)
assert hashlib.sha256(expected).hexdigest()==host['expected_sha256']
O.mkdir(parents=True)
r=dict(started_utc=utc(),status='building',physical_access=False,deployed=False,inputs={str(p):sha(p) for p in [P/'default.xbe',*[P/n for n in sources],K/'build001.py',K/'candidate.py',K/'host001.json',K.parent/'image-extent519/extent.py',K.parent/'image-extent519/final-review.json',*tools]},commands=[])
def save():OUT.write_bytes((json.dumps(r,indent=2)+'\n').encode())
def run(cmd):
    r['commands'].append(cmd);save()
    with (O/'build.log').open('ab') as f:subprocess.run(cmd,cwd=O,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=60)
try:
    changes=0
    for n in sources:
        old=(P/n).read_bytes();b=old.replace(candidate.OLD,candidate.NEW);changes+=old.count(candidate.OLD)
        assert b.replace(candidate.NEW,candidate.OLD)==old
        (O/n).write_bytes(b)
    assert changes==5
    run(['x86_64-linux-gnu-gcc-12','-m32','-nostdinc','-DASSEMBLER','-c','xbeboot.S','-o','xbeboot.o'])
    run(['ld','-m','elf_i386','-Ttext','0x10000','-Tdata','0x94c20','-e','entry510_trampoline','xbeboot.o','-o','wrapper.elf'])
    run(['objcopy','-O','binary','wrapper.elf','wrapper.bin'])
    symbols=subprocess.check_output(['nm','-n','wrapper.elf'],cwd=O,text=True,timeout=20);(O/'symbols.txt').write_bytes(symbols.encode())
    sy={v[2]:int(v[0],16) for line in symbols.splitlines() if len(v:=line.split())==3}
    assert sy['entry510_trampoline']==0x11100 and sy['entry503_gate']==0x94aff and sy['_end']==extent.END
    raw=(O/'wrapper.bin').read_bytes();assert len(raw)==extent.SIZE and not any(raw[0x3000:0x84000])
    b=bytearray(parent[:len(raw)]);b[4096:]=raw[4096:];b[0x3000:0x84000]=parent[0x3000:0x84000]
    for at,value in zip(extent.FIELDS,(len(b),len(b)-4096,len(b)-4096)):struct.pack_into('<I',b,at,value)
    b[extent.DIGEST]=extent.digest(b)
    assert bytes(b)==expected;candidate.validate(bytes(b),parent)
    (O/'default.xbe').write_bytes(b)
    (O/'disassembly.txt').write_bytes(subprocess.check_output(['objdump','-d','-Mintel','wrapper.elf'],cwd=O,timeout=20))
    for n,h in r['inputs'].items():assert sha(Path(n))==h,n
    r.update(status='compiled',bytes=len(b),sha256=sha(O/'default.xbe'),raw_linked_bytes=len(raw),wrapper_symbols=sy,source_parent_reconstruction=True,full_expected_binary_exact=True,namespace_offsets=candidate.offsets(parent),removed_parent_bytes=len(parent)-len(b),changed_prefix_offsets=[i for i in range(len(b)) if b[i]!=parent[i]],build_log=(O/'build.log').read_text())
except BaseException:r.update(status='failed',error=traceback.format_exc());raise
finally:
    r.update(finished_utc=utc(),files={str(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in O.iterdir() if p.is_file()});save()
    print(json.dumps({n:r[n] for n in ['status','physical_access','deployed','sha256'] if n in r}))
