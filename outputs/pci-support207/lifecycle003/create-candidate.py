"""Narrow NT5 START compatibility correction from the retained live resource trace."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;old=k.parent/'lifecycle002';policy=k.parent/'ownership001'
names={'xwnrsc.c':'xwnrsc.c','resources.h':'resources.h','install.c':'install.c','probe.c':'probe.c','restart.h':'restart.h','power-test.h':'power-test.h','remove-test.h':'remove-test.h','resource-log.h':'resource-log.h','xwnrsc.inf':'xwnrsc.inf','Build-004.ps1':'Build-001.ps1','review-build004.py':'review-build.py','prepare-emulator.py':'prepare-emulator.py','run-emulator.py':'run-emulator.py','audit-emulator.py':'audit-emulator.py','review-pnp.py':'review-pnp.py','Prepare-Emulator001.ps1':'Prepare-Emulator001.ps1','Run-Emulator001.ps1':'Run-Emulator001.ps1','Audit-Pnp001.ps1':'Audit-Pnp001.ps1','Wait-Audit001.ps1':'Wait-Audit001.ps1'}
for src,dst in names.items():
    p=k/dst;assert not p.exists()
    s=(old/src).read_text(encoding='utf-8').replace('lifecycle002','lifecycle003').replace('xwnpcilife2','xwnpcilife3').replace('build004','build001').replace('compiler004','compiler001').replace('build-review004','build-review001').replace('4754','4764').replace('4756','4766')
    if dst=='xwnrsc.inf':s=s.replace('0.1.0.222','0.1.0.223')
    if dst=='resources.h':
        s=s.replace('xwn_r32(p+12)!=0x00010001 ||','(xwn_r32(p+12)!=0x00010001 && xwn_r32(p+12)!=0) ||')
        s=s.replace('if(d[2]!=1 || d[3] || xwn_r32(d+8))', '/* Live NT5 START carries IO|16_BIT|POSITIVE_DECODE (0x31). */\n            if((d[2]!=1 && d[2]!=0x31) || d[3] || xwn_r32(d+8))')
    p.write_text(s,encoding='utf-8',newline='\n')
(k/'.gitattributes').write_text('* -text whitespace=cr-at-eol\n')
for name in ('resource-tests.h','vectors.h'):(k/name).write_bytes((policy/name).read_bytes())
trace=json.loads((old/'emulator001/resource-trace.json').read_text())
assert trace['sha256']=='1f9def3405f4786c6068d9176c701df3ea5e4ae39e7ec5c99dd51d9f08d7aeb0'
r=next(r for r in trace['records'] if r['stage']==3)
assert r['first_hex']==r['second_hex']
data=bytes.fromhex(r['first_hex'])
(k/'start-vector.h').write_text('/* Captured raw and translated NT5 START lists; identical. */\nstatic const unsigned char start_vector[]={'+','.join('0x%02x'%b for b in data)+'};\n')
(k/'input.json').write_text(json.dumps(dict(trace_sha256=trace['sha256'],trace_json_sha256=hashlib.sha256((old/'emulator001/resource-trace.json').read_bytes()).hexdigest(),change='Accept observed version/revision0/0 and I/O flags0x31; retain BootConfig1/1 and0x01; all address/count/length/type checks unchanged.'),indent=2)+'\n')
