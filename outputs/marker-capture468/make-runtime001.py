"""Fresh owned success and explicitly debugger-injected refusal runs."""
from pathlib import Path
K=Path(__file__).resolve().parent;P=K.parent/'marker-handoff466'
assert not (K/'Run001.ps1').exists()
def common(s):
 return s.replace('xwn466','xwn468').replace('marker466','capture468').replace('XWNBoot466a','XWNBoot468a').replace('5664','5684').replace('5665','5685').replace('5666','5686').replace('5667','5687').replace('preparation002','preparation001').replace('source-review002','source-review001')
for a,z in [('Invoke002.ps1','Invoke.ps1'),('close-host.py','close-host.py'),('protocol003.py','protocol003.py'),('start-owned.ps1','start-owned.ps1')]:
 (K/z).write_text(common((P/a).read_text()))
s=(P/'prepare002.py').read_text().replace('xwn466/build001','xwn468/build001').replace('xwn466/preparation002','xwn468/preparation001').replace("K/'preparation002.json'","K/'preparation001.json'")
s=s.replace("K/'preparation001.json'","K/'preparation001.json'",1)
s=s.replace("prior=json.loads((K/'preparation001.json').read_text())","prior=json.loads((K.parent/'marker-handoff466/preparation001.json').read_text())")
s=s.replace('../preparation001/seed.qcow2','../../xwn466/preparation001/seed.qcow2').replace('XWNBoot466a','XWNBoot468a')
(K/'prepare001.py').write_text(s)
for idx in ('001','002'):
 (K/f'emu{idx}').mkdir()
 s=common((P/'Run003.ps1').read_text()).replace('emu003','emu'+idx).replace('Invoke002.ps1','Invoke.ps1')
 (K/f'Run{idx}.ps1').write_text(s)
 s=common((P/'trace003.py').read_text()).replace('emu003','emu'+idx).replace('trace003','trace'+idx)
 if idx=='002':
  s=s.replace('from marker_decode import success','from marker_decode import success\nfrom refusal_decode002 import decode_refusal')
  a=s.index("    report=capture(sym['diag_record']");z=s.index('except BaseException as e:',a)
  s=s[:a]+'''    # Explicit intervention: model a first-transaction completion error. This
    # exercises actual refusal serialization, never qualifies physical status.
    injected=struct.pack('<24I',0x354b524d,1,96,1,0xff,5,0,1,0x20,2,1000,0,1200,0,0,0,0x20,0,0,4,0,3,1,0)
    r['intervention']=dict(kind='debugger writes modeled marker and refusal entry registers',
       hardware_status_naturally_observed=False,bytes=injected.hex())
    r['guest_memory_or_register_writes']=True;save()
    assert g.ask(f"M{sym['before_marker_record']:x},60:"+injected.hex())=='OK'
    regs=bytearray.fromhex(g.ask('g'))
    struct.pack_into('<I',regs,0,5)
    struct.pack_into('<I',regs,32,sym['diag_reboot'])
    assert g.ask('G'+regs.hex())=='OK'
    advance(sym['refusal_snapshot_ready'],'snapshot_before_cleanup')
    snap=capture(sym['refusal_record'],192,'refusal-snapshot')
    assert snap[80:176]==injected
    r['snapshot_decoded']=decode_refusal(snap)
    advance(sym['refusal_reboot'],'after_fallback_close_before_reboot')
    final=capture(sym['refusal_record'],192,'refusal-after-file-calls')
    assert final==snap
    assert capture(sym['before_marker_record'],96,'live-marker-after-file-calls')==injected
    r.update(passed=True,historical_physical_failure_reproduced=False,
             stopped_before_boot_device=True,windows_started=False,
             actual_emulator_markers=1,actual_loader_executed=False,
             injected_refusal=True,immutable_snapshot=True)
    save()
'''+s[z:]
 (K/f'trace{idx}.py').write_text(s)
 s=common((P/'collect003.py').read_text()).replace('emu003','emu'+idx).replace('cold003','cold'+idx)
 if idx=='002':
  s=s.replace('from decode import decode','from decode import decode\nfrom refusal_decode002 import decode_refusal')
  s=s.replace("    assert decoded['preparation_verified']", """    assert decoded['preparation_verified']
    refusal=w.read('Applications/XWNBoot468a/refusal.bin')
    (P/'refusal.bin').write_bytes(refusal)
    trace=json.loads((K/'emu002/trace.json').read_text())
    expected=Path(next(v['private_file'] for v in trace['reads'] if v['label']=='refusal-snapshot').replace('C:/','/mnt/c/')).read_bytes()
    assert refusal==expected
    decode_refusal(refusal)""")
  s=s.replace('r=dict(candidate_exact=True,',"r=dict(injected_refusal=True,refusal_memory_disk_exact=True,refusal=decode_refusal(refusal),candidate_exact=True,")
 (K/f'collect{idx}.py').write_text(s)
 (K/f'protected{idx}.py').write_text(common((P/'protected003.py').read_text()).replace('emu003','emu'+idx))
 s=common((P/'preflight003.py').read_text()).replace('emu003','emu'+idx).replace('from refusal_decode import','from refusal_decode002 import').replace('len(data)==96','len(data)==192')
 a=s.index("sample=Path(");z=s.index('for p in K.glob',a)
 s=s[:a]+"review=json.loads((K/'source-review001.json').read_text());assert review['passed']\n"+s[z:]
 (K/f'preflight{idx}.py').write_text(s)
