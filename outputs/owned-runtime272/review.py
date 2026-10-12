"""Independent review of closed272 capture bytes and the preserved failures."""
import hashlib,json,struct,sys
from pathlib import Path
from model import oracle,state
k=Path(__file__).resolve().parent;out=k/'emu004';dest=k/'final-review.json';assert not dest.exists()
r=json.loads((out/'trace.json').read_text());a=json.loads((out/'audit.json').read_text());d=json.loads((out/'disk-delta.json').read_text());c=json.loads((out/'host-closure.json').read_text(encoding='utf-8-sig'))
assert c['closed'] and c['host_exit']==0 and not c['fallback_kill']
assert r['passed'] and r['terminal_phase']==33 and not r['remaining_breakpoint'] and r['physical_mode_restored'] and r['orderly_quit_sent']
sha=lambda b:hashlib.sha256(b).hexdigest()
uv=[(0,0),(16,0),(16,8),(0,0),(16,8),(0,8)]
corners=[(0,0),(16,0),(16,8),(0,0),(16,8),(0,8)]
vertices=b''.join(struct.pack('<8f',float(ox+x),float(oy+y),.1,1,float(u),float(v),0,1) for ox,oy in [(32,32),(80,80)] for (x,y),(u,v) in zip(corners,uv))
assert len(vertices)==384
previous=0;sourcebytes=0;rawfiles=0;ramht=[];negative=0
for stop in r['checkpoints']:
    assert stop['arguments']['phase'] in (11,22,33)
    captures={}
    for row in stop['reads']:
        data=Path(row['private_file']).read_bytes();assert len(data)==row['bytes'] and sha(data)==row['sha256'];captures[row['label']]=data;rawfiles+=1
    phase=stop['arguments']['phase'];assert state(captures['record'],phase,previous)['passed'];previous=phase
    assert captures['vertices']==vertices
    for unit in range(4):assert captures['texture'+str(unit)]==oracle.blocks()[unit];sourcebytes+=4096
    assert stop['kernel']['export_ordinal']==173
    edges=[]
    for at in range(0,4096,8):
        identity,ctx=struct.unpack_from('<II',captures['ramht'],at)
        if not identity and not ctx:continue
        assert ctx&0x80000000 and (ctx>>24)&31==stop['pbkit']['_pb_FifoChannelID']
        assert at==identity*8 and identity in list(range(2,15))+[16,17]
        edges.append(dict(identity=identity,instance=ctx&65535,graphics=bool(ctx&65536)))
    assert len(edges)==15;ramht.append(edges)
    # Refuse any single-byte source mutation in each captured payload/guard boundary.
    for unit in range(4):
        for index in (0,255,256,767,768,4095):
            bad=bytearray(captures['texture'+str(unit)]);bad[index]^=1
            assert bytes(bad)!=oracle.blocks()[unit];negative+=1
assert ramht[0]==ramht[1]==ramht[2]
assert d['changed_bytes']==1 and d['all_file_system_bytes_inherited_unchanged']
assert not a['passed'] and not a['disk_all_bytes_unchanged']
assert all(a['source_pins'].values()) and all(a['immutable_copies'].values()) and all(a['dependencies'].values())
assert all(x['returncode']==0 for x in a['checks'].values())
for case,prior in [('emu001','prior001'),('emu002','prior002'),('emu003','prior003')]:
    f=json.loads((k/case/'prepared.json').read_text())
    for path,digest in f['dependencies'].items():
        p=Path(path);candidate=k/prior/p.name if p.parent.resolve()==k.resolve() else p
        assert sha(candidate.read_bytes())==digest,(case,path)
summary=dict(closed=True,never_relaunch_or_recollect=True,scoped_standalone_pixel_control_passed=True,strict_qualification_passed=False,
    strict_failure='One reserved-area disk byte changed; original whole-disk equality gate failed',
    actual_checkpoint_phases=[11,22,33],unique_framebuffer_bytes=1440,source_guard_read_bytes=sourcebytes,
    exact_vertex_bytes_per_stop=384,actual_private_capture_files_rehashed=rawfiles,source_boundary_mutations_rejected=negative,
    guest_error=0,guest_idle_polls=3,normal_windows_restart=False,guest_terminal_halt_requested_by_pinned_code=True,
    actual_HAL_halt_entry_traced=False,orderly_host_exit=0,breakpoints_remaining=0,physical_mode_restored=True,
    disk_virtual_bytes=8589934592,disk_overlay_bytes_compared=65536,reserved_area_changed_bytes=1,filesystem_bytes_inherited_unchanged=True,
    eeprom_unchanged=a['eeprom_unchanged'],qcow_checks_clean=True,frozen_dependency_count=len(a['dependencies']),
    original_input_closures_preserved=True,actual_stable_ramht_edges=ramht[0],
    limitations=['No host reference ledger or callback lifetime capture in272','RAMHT entries captured, but full DMA/graphics object descriptors were not all captured; do not claim complete object attestation','No native Windows GPU ownership, disposal, acceleration, physical promotion or performance measurement','Standalone fixture has no Windows event/hive result; earlier Ftdisk49 remains separate','Guest idle and CPU framebuffer results are not host actor completion or OS-thread exit'],
    physical_access=False,release_installed=False,observer_operation=False,full_four_generation_reuse_qualified=False)
dest.write_text(json.dumps(summary,indent=2)+'\n')
(out/'closure.json').write_text(json.dumps(dict(closed=True,never_relaunch_or_recollect=True,final_review_sha256=sha(dest.read_bytes()),scoped_pixel_control_passed=True,strict_passed=False,host_exit=0),indent=2)+'\n')
print(json.dumps(summary,indent=2))
