"""Review fresh236 source/fixture boundaries before its only launch."""
import ast,hashlib,json,shutil,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'prelaunch-review001.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
assert read(k/'preparation-host001.json')['closed'] and read(k/'preparation-host001.json')['passed']
assert read(k/'parsing-test003.json')['passed'] and read(k/'guard-test001.json')['passed']
assert read(k/'parsing-test003.json')['source_sha256']==sha(k/'parsing.py')
assert read(k/'guard-test001.json')['source_sha256']==sha(k/'trace.py')
inv=read(k/'inventory001.json');assert inv['passed'] and not inv['new_emulator_build']
parent=read(k.parent/'xemu-wait-snapshot234/emulator-frozen.json')
for name,digest in parent.items():assert sha(ws/name)==digest,name
build=read(k.parent/'xemu-wait-snapshot234/build001.json');assert build['passed'] and build['borrowed_sources_restored']
assert build['executable_sha256']=='7d953556b2bd4155f43779250fb2240e5d8f7f656525e9c33fdbad6ccf1a976e'
src=k/'artifacts/inputs/source'
for name,digest in inv['files'].items():
 if name.startswith(('gdbstub/','accel/','system/','target/','include/')):assert sha(src/name)==digest
assert 'gdb_stop_before_watchpoint =' not in (src/'target/i386/cpu.c').read_text()
assert 'cpu->cflags_next_tb = 1 | CF_NOIRQ' in (src/'accel/tcg/watchpoint.c').read_text()
trace=(k/'trace.py').read_text();tree=ast.parse(trace)
assert "arm(2,0xfd400100,4)" in trace and "journal_ack(report,candidates[0]['value'])" in trace
assert trace.count("ftp.sendcmd(row['command'])")==1
assert 'Qqemu.PhyMemMode:1' not in trace and 'xwn-preserve232 true' not in trace
assert 'g.write(' not in trace and "ask('G" not in trace and "ask('M" not in trace
assert "r['mode_verification_error']" in trace and "quarantined=True" in trace and 'armed.copy()' in trace
assert 'overall=time.monotonic()+60' in trace
assert 'guest_trace_scope_passed' in (k/'audit-emulator.py').read_text()
assert "r['preservation_trace_scope_passed']" not in (k/'audit-emulator.py').read_text()
observer=(k/'supervise-emulator.py').read_text()
pre=observer[:observer.index("assert trace['loader_launch']['status']=='accepted'")]
assert 'f=connect(deadline)' not in pre and 'ftp.login(' not in pre
assert read(k/'connection-test001.json')['passed']
fixture=read(k/'fixture-trace001.json');assert fixture['prepared'] and not fixture['inherited_null_policy']
assert sha(Path(fixture['fixture_path_windows']))==fixture['seed_sha256']
assert not (k/'trace001/runner-start.json').exists()
assert not Path('E:/Codex-private-artifacts/xbox-windows-feasibility/guest236-runs/nt5-guest236-trace001').exists()
capacity={drive:shutil.disk_usage(drive+'/').free for drive in ['C:','E:']};assert capacity['C:']>=20*1024**3
dest.write_text(json.dumps(dict(passed=True,source_sha256=sha(Path(__file__)),emulator_sha256=build['executable_sha256'],no_new_emulator_or_driver_build=True,fresh_fixture_sha256=fixture['seed_sha256'],after_write_boundary_is_reconstructed=True,guard_checks=read(k/'guard-test001.json')['checks'],parser_checks=read(k/'parsing-test003.json')['checks'],capacity_free_bytes=capacity,physical_access=False,guest_launch=False),indent=2)+'\n')
print('236 prelaunch review PASS')
