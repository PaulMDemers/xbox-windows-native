"""Create a new owned emulator controller from closed414 transport, never rerun414."""
import json
from pathlib import Path
K=Path(__file__).resolve().parent;P=K.parent/'cromwell-devices414'
assert not (K/'Invoke.ps1').exists()
for n in ['start-owned.ps1','protocol.py']:(K/n).write_bytes((P/n).read_bytes())
s=(P/'Invoke.ps1').read_text().replace('E:/xwn414','C:/xwn466').replace('/mnt/e/xwn414','/mnt/c/xwn466')
s=s.replace('E:/xwn412/preparation002/fresh.qcow2','C:/xwn466/preparation001/seed.qcow2').replace('../../../xwn412/preparation002/fresh.qcow2','../../preparation001/seed.qcow2')
s=s.replace('5497','5667').replace('E:/xwn405/instances','C:/xwn466/instances').replace('E:/xwn405/scratch','C:/xwn466/scratch')
(K/'Invoke.ps1').write_text(s)
(K/'close-host.py').write_text((P/'close-host.py').read_text().replace('5494','5664'))
s=(P/'Run.ps1').read_text().replace("../handoff-trace412/preparation002.json","preparation001.json")
s=s.replace("if(-not $f.prepared)","if($f.status -ne 'prepared')").replace('E:/xwn412/preparation002/fresh.qcow2','C:/xwn466/preparation001/seed.qcow2').replace('$f.fixture_sha256','$f.seed_sha256')
s=s.replace("if((Get-PSDrive C).Free-16MB -lt 20GB -or (Get-PSDrive E).Free-128MB -lt 20GB)","if((Get-PSDrive C).Free-768MB -lt 20GB)")
s=s.replace('nt5-cromwell414-emu001','nt5-marker466-emu001').replace('-InstanceTask windows-native-fresh405-emu001','-InstanceTask windows-native-marker466-emu001')
s=s.replace('5496','5666').replace('5494','5664').replace('5495','5665')
(K/'Run.ps1').write_text(s)
s=(P/'trace.py').read_text().replace('import ast','import ast\nimport io').replace('from frame import geometry','from marker_decode import success')
s=s.replace('E:/xwn414','C:/xwn466').replace('nt5-cromwell414-emu001','nt5-marker466-emu001').replace('5494','5664').replace('5495','5665').replace('5496','5666')
a=s.index("prep = json.loads(");z=s.index('utc = lambda:',a)
s=s[:a]+'''build=json.loads((K/'build001.json').read_text())
sym=build['wrapper_symbols'];stub=build['stub_symbols']
review=json.loads((K/'source-review002.json').read_text());assert review['passed']
xbe=Path('C:/xwn466/build001/default.xbe').read_bytes()
sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(xbe)==build['sha256']
payload=xbe[0x3000:0x3000+build['payload_bytes']]
'''+s[z:]
s=s.replace('EIP|ESP|ESI|EDX|ECX|EFL|CR0|CR3|CR4','EIP|ESP|EAX|EBX|EBP|EDI|ESI|EDX|ECX|EFL|CR0|CR3|CR4')
# Stage in an absent private directory, verify bytes, issue SITE once.
anchor="    mon('stop')\n    stopped = True\n    g = Remote(5665)"
upload='''    r['stage']={'directory':'E:/Applications/XWNBoot466a','fresh':False}
    f.cwd('/E/Applications')
    names=[];f.retrlines('NLST',names.append)
    assert 'XWNBoot466a'.casefold() not in [n.rsplit('/',1)[-1].casefold() for n in names]
    f.mkd('XWNBoot466a');f.cwd('XWNBoot466a')
    r['stage']['fresh']=True;save()
    f.storbinary('STOR default.xbe',io.BytesIO(xbe))
    check=bytearray();f.retrbinary('RETR default.xbe',check.extend)
    assert bytes(check)==xbe;r['stage']['readback_sha256']=sha(check);save()
'''
assert s.count(anchor)==1;s=s.replace(anchor,upload+anchor)
s=s.replace(r'SITE EXEC E:\Applications\XWNEBoot\default.xbe',r'SITE EXEC E:\Applications\XWNBoot466a\default.xbe')
s=s.replace("'original_entry'","'diagnostic_entry'").replace("'loaded-original-wrapper'","'loaded-diagnostic-wrapper'")
s=s.replace("capture(0x13000, 288316, 'loaded-original-payload') == xbe[0x3000:0x3000+288316]","capture(0x13000, len(payload), 'loaded-diagnostic-payload') == payload")
a=s.index("    cromwell = advance(");z=s.index('except BaseException as e:',a)
s=s[:a]+'''    # Watch both success and refusal without retrying either marker.
    advance(sym['diag_handoff'],'before_first_marker')
    bp(sym['diag_reboot'],True)
    bp(sym['diag_marker_ready'],True)
    stopped=False;g.send('c');reply=g.recv(35);stopped=True
    first=registers('first_marker_terminal');assert reply.startswith(('T','S'))
    raw=capture(sym['before_marker_record'],96,'first-marker-record')
    r['first_marker_raw_words']=list(struct.unpack('<24I',raw));save()
    assert first['registers']['EIP']==sym['diag_marker_ready'],'first marker refused'
    r['first_marker']=success(raw,1)
    bp(sym['diag_reboot'],False);bp(sym['diag_marker_ready'],False)
    report=capture(sym['diag_record'],176,'primary-memory-report');words=struct.unpack('<44I',report)
    loader=advance(0x1000000,'before_original_loader_cli')['registers']
    for i,n in enumerate(['EDI','ESI','EBP','ESP','EBX','EDX','ECX','EAX']):
        assert loader[n]==words[32+i]+(4 if n=='ESP' else 0),(n,loader[n],words[32+i])
    assert loader['EFL']&0xed5==words[28]&0xed5
    assert capture(loader['ESI'],len(payload),'physical-source-before-copy',True)==payload
    cromwell=advance(0x2600000,'cromwell_entry')
    assert not cromwell['registers']['CR0']&0x80000000
    assert capture(0x2600000,len(payload),'relocated-cromwell')==payload
    pre=advance(0x26000f0,'before_stack_install')['registers']
    bp(stub['after_stack_failed'],True);bp(stub['after_stack_ready'],True)
    stopped=False;g.send('c');reply=g.recv(35);stopped=True
    second=registers('second_marker_terminal');assert reply.startswith(('T','S'))
    raw=capture(stub['after_stack_record'],96,'second-marker-record')
    r['second_marker_raw_words']=list(struct.unpack('<24I',raw));save()
    assert second['registers']['EIP']==stub['after_stack_ready'],'second marker refused'
    r['second_marker']=success(raw,2)
    for n in ['EAX','EBX','ECX','EDX','ESI','EDI','EBP']:
        assert pre[n]==second['registers'][n],n
    assert second['registers']['ESP']==0x2800000
    assert pre['EFL']==second['registers']['EFL']
    bp(stub['after_stack_failed'],False);bp(stub['after_stack_ready'],False)
    advance(0x26000f5,'original_continuation')
    assert capture(0x26000f5,32,'original-continuation-code')==payload[0xf5:0x115]
    r.update(passed=True,historical_physical_failure_reproduced=False,
             stopped_before_boot_device=True,windows_started=False,
             actual_emulator_markers=2,actual_loader_executed=True,
             actual_stack_installed=True,post_stack_registers_flags_preserved=True)
    save()
'''+s[z:]
(K/'trace.py').write_text(s)
(K/'emu001').mkdir()
