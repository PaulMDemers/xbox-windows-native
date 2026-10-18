# SPDX-License-Identifier: MIT
"""Independent actual source/object/ELF/raw/XBE review, with inverse byte checks."""
import datetime,hashlib,importlib.util,json,struct,subprocess,sys,traceback
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('C:/xwn516/build001');N=Path('C:/xwn520/build001');R=Path('C:/xwn520/review001');OUT=K/'review001.json'
assert not R.exists() and not OUT.exists();R.mkdir()
sys.path.insert(0,str(K.parent/'data-layout515'));import elf32
sp=importlib.util.spec_from_file_location('structure520',K.parent/'loader-comparison509/inspect.py');xm=importlib.util.module_from_spec(sp);sp.loader.exec_module(xm)
sha=lambda b:hashlib.sha256(b).hexdigest();pins={}
def load(p):
    p=Path(p);b=p.read_bytes();pins[str(p.resolve())]=dict(bytes=len(b),sha256=sha(b));return b
def js(p):return json.loads(load(p))
def mapped(n):return Path(n.replace('/mnt/c/','C:/',1))
def digest(b):return hashlib.sha1(struct.pack('<I',len(b)-4096)+b[4096:]).digest()
def inverse(b,parent,places):
    if len(b)!=544096:raise ValueError('actual length')
    if tuple(struct.unpack_from('<I',b,o)[0] for o in (0x10c,0x350,0x358))!=(544096,540000,540000):raise ValueError('actual header lengths')
    if b[0x36c:0x380]!=digest(b):raise ValueError('actual digest')
    q=bytearray(b)
    for a in places:
        if q[a:a+11]!=b'XWNBoot520a':raise ValueError('actual namespace')
        q[a:a+11]=b'XWNBoot516a'
    for a,n in [(0x10c,4),(0x350,4),(0x358,4),(0x36c,20)]:q[a:a+n]=parent[a:a+n]
    if q!=parent[:len(b)]:raise ValueError('unapproved actual byte')
    return True
r=dict(passed=False,started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),physical_access=False,runtime_executed=False)
try:
    for p in [K/'review001.py',K/'candidate.py',K.parent/'data-layout515/elf32.py',K.parent/'loader-comparison509/inspect.py']:load(p)
    prior=js(K.parent/'entry-colocated516/build001.json');build=js(K/'build001.json');host=js(K/'host001.json')
    assert build['status']=='compiled' and host['passed']
    for manifest in [prior,build]:
        for n,row in manifest['files'].items():assert sha(load(mapped(n)))==row['sha256']
    for n,h in host['inputs'].items():assert sha(load(n))==h
    sources=['xbeboot.S','xbe.S','font.S','witness.S','context.S','capture.S','entry.S','combined.S','indicator.S']
    changes=0
    for n in sources:
        a=load(P/n);b=load(N/n);changes+=b.count(b'XWNBoot520a');assert b.replace(b'XWNBoot520a',b'XWNBoot516a')==a
    assert changes==5
    a=elf32.parse(load(P/'xbeboot.o'));b=elf32.parse(load(N/'xbeboot.o'))
    assert a['named']==b['named'] and a['symbols']==b['symbols'] and a['relocations']==b['relocations']
    t=a['named']['.text'];d=a['named']['.data']
    for n in ['.text','.data']:
        i=a['named'][n];assert b['data'](b['sections'][i]).replace(b'XWNBoot520a',b'XWNBoot516a')==a['data'](a['sections'][i])
    ae=elf32.parse(load(P/'wrapper.elf'));be=elf32.parse(load(N/'wrapper.elf'));assert ae['symbols']==be['symbols']
    linked,ledger=elf32.relocated(b,{t:0x10000,d:0x94c20});_,oldledger=elf32.relocated(a,{t:0x10000,d:0x94c20});assert ledger==oldledger and len(ledger)==395
    for n,i in [('.text',t),('.data',d)]:assert linked[i]==be['data'](be['sections'][be['named'][n]])
    raw=load(N/'wrapper.bin');oldraw=load(P/'wrapper.bin')
    assert raw==linked[t]+bytes(8)+linked[d] and len(raw)==544096
    assert raw.replace(b'XWNBoot520a',b'XWNBoot516a')==oldraw
    parent=load(P/'default.xbe');actual=load(N/'default.xbe')
    assert sha(parent)=='a272c18d32f96719ddf5ec07dcc551f74165f797b8247b361c1a4e3b3d84da1d'
    assert len(parent)==545088 and sha(actual)==build['sha256']==host['expected_sha256']
    places=[];start=0
    while True:
        at=parent.find(b'XWNBoot516a',start)
        if at<0:break
        places.append(at);start=at+11
    assert len(places)==5 and places==host['namespace_offsets'] and actual.count(b'XWNBoot520a')==5
    assert inverse(actual,parent,places)
    assert actual[0x84877:0x84c18]==parent[0x84877:0x84c18] and actual[0x1100:0x1105]==parent[0x1100:0x1105]
    assert actual[0x3000:0x84000]==parent[0x3000:0x84000]
    structure=xm.inspect(actual);before=xm.inspect(parent)
    assert structure['rounded_image_end']==0x95000 and before['rounded_image_end']==0x96000
    assert structure['entry']==before['entry']==0x11100
    assert structure['section']['flags']==before['section']['flags']==7
    for n in ['imports','tls_words','tls_address','tls_bytes_sha256','certificate_sha256']:assert structure[n]==before[n]
    assert load(N/'build.log')==load(P/'build.log')==b'/usr/bin/x86_64-linux-gnu-ld.bfd: warning: wrapper.elf has a LOAD segment with RWX permissions\n'
    current_tool=subprocess.check_output(['wsl','-d','Ubuntu','--','sha256sum','/usr/bin/objdump'],text=True,timeout=20).split()[0];assert current_tool==build['inputs']['/usr/bin/objdump']
    text=subprocess.check_output(['wsl','-d','Ubuntu','--','objdump','-dw','-Mintel','--start-address=0x94877','--stop-address=0x94c18','/mnt/c/xwn520/build001/wrapper.elf'],timeout=20)
    prior_dis=load('C:/xwn516/review001/new-diagnostic.txt')
    assert text.replace(b'/mnt/c/xwn520/',b'/mnt/c/xwn516/')==prior_dis
    (R/'diagnostic.txt').write_bytes(text)
    positions=set(range(0x84877,544096))|set(range(4096,544096,4096))|set(range(0x128,0x12c))|set(range(0x348,0x35c))
    for at in [0x10c,*places]:positions.update(range(at,at+(11 if at in places else 4)))
    rejected=0
    for at in sorted(positions):
        bad=bytearray(actual);bad[at]^=1;bad[0x36c:0x380]=digest(bad)
        try:inverse(bytes(bad),parent,places)
        except ValueError:rejected+=1
        else:raise AssertionError(('actual mutation accepted',at))
    (R/'relocations.json').write_bytes((json.dumps(ledger,indent=2)+'\n').encode())
    for n,row in pins.items():assert sha(Path(n).read_bytes())==row['sha256']
    r.update(passed=True,bytes=len(actual),sha256=sha(actual),source_reconstructions=9,symbols_unchanged=True,relocations_unchanged=395,diagnostic_code_bytes_unchanged=929,trampoline_unchanged=True,raw_wrapper_namespace_only=True,full_actual_image_inverse_passed=True,removed_bytes=992,payload_unchanged=True,namespace_offsets=places,actual_mutations_rejected=rejected,actual_structure=structure,inherited_intermediate_RWX_warning_retained=True,final_XBE_permissions_unchanged=True,TLS_runtime_unknown=True,actual_objdump_sha256=current_tool,deployed=False)
except Exception:r['failure']=traceback.format_exc()
finally:
    r.update(finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),inputs=pins,private_files={str(p):dict(bytes=p.stat().st_size,sha256=sha(p.read_bytes())) for p in R.iterdir() if p.is_file()})
    OUT.write_bytes((json.dumps(r,indent=2)+'\n').encode());print(json.dumps({n:r[n] for n in ['passed','failure','sha256','actual_mutations_rejected'] if n in r}))
if not r['passed']:raise SystemExit(1)
