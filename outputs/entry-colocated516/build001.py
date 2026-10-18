# SPDX-License-Identifier: MIT
"""Exact510 child with data at94c20, fresh namespace, unchanged image extents."""
import datetime,hashlib,json,os,shutil,subprocess,sys,traceback
from pathlib import Path
import candidate
from candidate import layout
K=Path(__file__).resolve().parent;P=Path('/mnt/c/xwn510/build001');O=Path('/mnt/c/xwn516/build001');OUT=K/'build001.json'
assert os.environ.get('XWN_BUILD_LEASE')=='held' and not OUT.exists() and not O.exists()
assert shutil.disk_usage('/mnt/c').free-32*1024**2>=20*1024**3
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_bytes());utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def mapped(n):return Path(n.replace('C:\\','/mnt/c/').replace('C:/','/mnt/c/').replace('\\','/'))
prior=read(K.parent/'entry-trampoline510/build001.json');host=read(K/'host001.json')
assert prior['status']=='compiled' and host['passed'] and host['closed']
for n,v in prior['files'].items():assert sha(Path(n))==v['sha256'],n
for n,h in host['inputs'].items():assert sha(mapped(n))==h,n
for n,row in host['private_files'].items():assert sha(mapped(n))==row['sha256'],n
sources=['xbeboot.S','xbe.S','font.S','witness.S','context.S','capture.S','entry.S','combined.S','indicator.S']
tools=[Path('/usr/bin')/n for n in ['x86_64-linux-gnu-gcc-12','as','ld','objcopy','objdump','nm']]
for p in tools:assert sha(p)==prior['inputs'][str(p)]
old=(P/'default.xbe').read_bytes();expected,ledger,t,d,offsets=candidate.prepare(old,(P/'xbeboot.o').read_bytes())
assert hashlib.sha256(expected).hexdigest()==host['expected_sha256']
O.mkdir(parents=True)
r=dict(started_utc=utc(),status='building',physical_access=False,deployed=False,inputs={str(p):sha(p) for p in [P/'default.xbe',P/'xbeboot.o',*[P/n for n in sources],K/'candidate.py',K/'build001.py',K/'host001.json',K.parent/'data-layout515/elf32.py',K.parent/'data-layout515/layout.py',*tools]},commands=[])
def save():OUT.write_bytes((json.dumps(r,indent=2)+'\n').encode())
def run(cmd):
    r['commands'].append(cmd);save()
    with (O/'build.log').open('ab') as f:subprocess.run(cmd,cwd=O,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=60)
try:
    changes=0
    for name in sources:
        src=(P/name).read_bytes();b=src.replace(candidate.OLD_NAME,candidate.NEW_NAME);changes+=src.count(candidate.OLD_NAME)
        assert b.replace(candidate.NEW_NAME,candidate.OLD_NAME)==src
        (O/name).write_bytes(b)
    assert changes==5
    run(['x86_64-linux-gnu-gcc-12','-m32','-nostdinc','-DASSEMBLER','-c','xbeboot.S','-o','xbeboot.o'])
    run(['ld','-m','elf_i386','-Ttext','0x10000','-Tdata','0x94c20','-e','entry510_trampoline','xbeboot.o','-o','wrapper.elf'])
    run(['objcopy','-O','binary','wrapper.elf','wrapper.bin'])
    symbols=subprocess.check_output(['nm','-n','wrapper.elf'],cwd=O,text=True,timeout=20);(O/'symbols.txt').write_bytes(symbols.encode())
    sy={v[2]:int(v[0],16) for line in symbols.splitlines() if len(v:=line.split())==3}
    assert sy['entry510_trampoline']==0x11100 and sy['entry503_gate']==0x94aff and sy['entry498_record']==layout.NEW
    raw=(O/'wrapper.bin').read_bytes();assert len(raw)==layout.NEW+layout.SIZE-layout.BASE and not any(raw[0x3000:0x84000])
    b=bytearray(old);b[4096:len(raw)]=raw[4096:];b[0x3000:0x84000]=old[0x3000:0x84000]
    b[0x36c:0x380]=layout.digest(b)
    assert bytes(b)==expected;candidate.validate(bytes(b),old,ledger,t,d,offsets)
    (O/'default.xbe').write_bytes(b)
    (O/'disassembly.txt').write_bytes(subprocess.check_output(['objdump','-d','-Mintel','wrapper.elf'],cwd=O,timeout=20))
    for n,h in r['inputs'].items():assert sha(Path(n))==h,n
    r.update(status='compiled',bytes=len(b),sha256=sha(O/'default.xbe'),raw_linked_bytes=len(raw),wrapper_symbols=sy,source_parent_reconstruction=True,full_expected_binary_exact=True,namespace_offsets=offsets,old_tail_preserved=True,changed_offsets=[i for i in range(len(b)) if b[i]!=old[i]],build_log=(O/'build.log').read_text())
except BaseException:r.update(status='failed',error=traceback.format_exc());raise
finally:
    r.update(finished_utc=utc(),files={str(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in O.iterdir() if p.is_file()});save()
    print(json.dumps({n:r[n] for n in ['status','physical_access','deployed','sha256'] if n in r}))
