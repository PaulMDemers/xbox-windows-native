"""Read-only review of the failed closed275 attempt; never completes missing pages."""
import hashlib,json,re,struct
from pathlib import Path
from backend import numbers
from objects import inspect,commands
from proof import vertices
k=Path(__file__).resolve().parent;out=k/'emu001';root=Path('E:/xwn275/emu001');dest=k/'final-review.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
t=read(out/'trace.json');c=read(out/'host-closure.json');a=read(out/'audit.json');d=read(out/'disk-delta.json');p=read(out/'prepared.json')
assert c['closed'] and c['host_exit']==0 and not c['fallback_kill']
assert not t['passed'] and 'PermissionError' in t['error'] and len(t['checkpoints'])==1
assert t['physical_mode_restored'] and not t['remaining_breakpoint'] and not t['resumed_after_teardown']
assert t['orderly_quit_sent'] and not t.get('cleanup_error') and not t.get('frontend_cleanup_error')
report=numbers(t['initial_report']);assert report['state']==6 and report['reason']==14
assert report['cpu0_count']==4 and report['cpu0_done']==1 and report['cpu0_reason']==0
assert report['cpu1_done']==0 and report['accounting']==report['shader_jobs_unknown']==report['pending']==0
assert report['cpu0_epoch']==1 and report['worker'] and report['cpu0_thread']!=report['worker']
assert numbers(t['frontend_reopened_report'])['state']==5
assert not t.get('terminal_request_may_be_accepted') and not list((root/'watch').iterdir())
stop=t['checkpoints'][0];assert stop['arguments']['phase']==11 and stop['pixel_check']['passed']
captures=[];by={}
for entry in stop['reads']:
    data=Path(entry['private_file']).read_bytes();assert len(data)==entry['bytes'] and hashlib.sha256(data).hexdigest()==entry['sha256']
    captures.append(dict(file=entry['private_file'],bytes=len(data),sha256=entry['sha256']));by[entry['label']]=data
assert by['vertices']==vertices()
result=inspect(by['ramht'],stop['pbkit'],stop['state_header'],lambda addr,n,label:by[label])
cmd=commands(by['pushbuffer-used'])
assert result==stop['objects'] and cmd==stop['push_commands']
negative=0
for handle in range(2,18):
    if handle==15:continue
    ramht=bytearray(by['ramht']);ramht[handle*8+6]^=1
    try:inspect(ramht,stop['pbkit'],stop['state_header'],lambda addr,n,label:by[label])
    except AssertionError:negative+=1
    else:raise AssertionError('Actual channel mutation accepted')
rows=[];pages=[]
for index,path in enumerate(sorted((out/'initial-pages').glob('*.txt'))):
    raw=path.read_bytes();text=raw.decode();h=numbers(text)
    assert h['page']==index and h['epoch']==1 and h['rows']==report['rows'] and h['pages']==report['pages']
    for n,values in re.findall(r'(?<!\w)r(\d+)=([0-9:]+)',text):
        assert int(n)==len(rows);row=list(map(int,values.split(':')));assert len(row)==8;rows.append(row)
    pages.append(dict(file=str(path),sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw)))
assert len(pages)<report['pages']
units=[r for r in rows if r[0]==3];bindings=[r for r in rows if r[0]==4];accounts=[r for r in rows if r[0]==5]
assert len(units)==4 and all(r[3]==0 for r in units)
assert len(bindings)==len(accounts)==report['bindings']
for u in units:
    ac=next(r for r in accounts if r[1]==u[2]);assert ac[2:5]==[2,1,1]
# These partial rows do not contain the acknowledged callback identity inventory.
assert not any(r[0]==17 for r in rows)
assert all(a['source_pins'].values()) and all(a['immutable_copies'].values()) and all(a['dependencies'].values())
assert a['eeprom_unchanged'] and all(x['returncode']==0 for x in a['checks'].values())
assert d['changed_bytes']==1 and d['all_file_system_bytes_inherited_unchanged']
r=dict(closed=True,never_relaunch_recollect_or_parent=True,scoped_unchanged_reuse_passed=False,strict_passed=False,
    failure='Initial zero-callback gate refused four live CPU callbacks; separately host atomic replace failed while reading immutable pages',
    callback_identities_captured=False,actual_initial_report=report,initial_pages_captured=len(pages),initial_pages_total=report['pages'],
    partial_rows=len(rows),partial_unit_rows=units,partial_binding_count=len(bindings),four_disabled_refs2_cache1_unit1=True,
    actual_descriptor_count=result['count'],descriptor_scope=result['scope'],actual_channel_mutations_rejected=negative,
    retained_command_evidence=cmd,source_guard_bytes=16384,independent_framebuffer_bytes=720,independent_vertex_bytes=384,
    private_captures_rehashed=len(captures),capture_manifest=captures,partial_page_manifest=pages,
    initial_ui_pages=len(t['ui_pages']),terminal_boundary_requested=False,observer_armed=False,release_installed=False,
    native_gpu_grant=False,performance_qualified=False,normal_guest_terminal=False,normal_windows_restart=False,
    orderly_host_exit=0,fallback_kill=False,frontend_reopened=True,breakpoints_removed=True,physical_mode_restored=True,
    strict_disk_equality=False,reserved_sector_changed_bytes=1,filesystem_bytes_inherited_unchanged=True,
    frozen_dependencies_exact=len(p['dependencies']),eeprom_unchanged=True,
    next='New observation-only collection of the missing callback identities with bounded atomic writer; do not remove the zero-count gate or run a release candidate')
dest.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({x:r[x] for x in ['closed','failure','partial_rows','private_captures_rehashed','actual_descriptor_count','frozen_dependencies_exact']},indent=2))
