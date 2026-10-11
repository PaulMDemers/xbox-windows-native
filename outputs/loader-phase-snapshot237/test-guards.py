"""Exercise actual source helpers with bounded failure adapters; no guest launch."""
import ast, datetime, ftplib, hashlib, json, os
from pathlib import Path

k = Path(__file__).resolve().parent
dest = k / 'guard-test001.json'
assert not dest.exists()
source = k / 'trace.py'
tree = ast.parse(source.read_text())
helpers = ast.Module(body=[n for n in tree.body if isinstance(n, ast.FunctionDef)
                          and n.name in ['wait_dashboard', 'restore_physical_mode']], type_ignores=[])
checks = 0

class Clock:
    def __init__(self): self.value = 0
    def monotonic(self): return self.value
    def sleep(self, seconds):
        assert 0 <= seconds <= .2
        self.value += seconds

class Remote:
    def __init__(self, reply, mode='0'): self.reply = reply; self.mode = mode; self.commands = []
    def ask(self, command):
        self.commands.append(command)
        if command == 'qqemu.PhyMemMode':
            if isinstance(self.mode, Exception): raise self.mode
            return self.mode
        if isinstance(self.reply, Exception): raise self.reply
        return self.reply

clock = Clock()
namespace = dict(ftplib=ftplib, time=clock, os=os, utc=lambda: 'host-test')
exec(compile(helpers, str(source), 'exec'), namespace)
restore = namespace['restore_physical_mode']
for reply in ['OK', 'E14', '', TimeoutError('uncertain reply')]:
    for read_mode in [False, True]:
        remote = Remote(reply)
        record = dict(physical_mode_restore_required=True, physical_read_mode=read_mode)
        success = restore(remote, record)
        assert success == (reply == 'OK')
        assert remote.commands == (['Qqemu.PhyMemMode:0','qqemu.PhyMemMode'] if reply == 'OK' else ['Qqemu.PhyMemMode:0'])
        assert record['physical_mode_restored'] == success
        assert record['physical_mode_restore_required'] == (not success)
        if success: assert not record['physical_read_mode']
        checks += 5
for mode in ['1', '', 'E14', TimeoutError('restore query lost')]:
    remote = Remote('OK', mode)
    record = dict(physical_mode_restore_required=True, physical_read_mode=True)
    assert not restore(remote, record)
    assert record['physical_mode_restore_required'] and record['physical_read_mode']
    assert not record['physical_mode_restored']
    checks += 3
remote = Remote('E14')
assert restore(remote, {}) and not remote.commands
checks += 1

class FTP:
    attempts = 0
    closes = 0
    fail_count = 0
    fail_stage = 'connect'
    def __init__(self, deadline): self.deadline = deadline
    def __enter__(self): FTP.attempts += 1; return self
    def __exit__(self, *args): FTP.closes += 1
    def budget(self): return self.deadline - clock.value
    def check(self, stage):
        assert self.deadline > clock.value
        if FTP.attempts <= FTP.fail_count and stage == FTP.fail_stage:
            raise ftplib.error_temp('bounded adapter failure')
    def connect(self, host, port, timeout):
        assert (host, port) == ('127.0.0.1', 4596) and 0 < timeout <= 6
        self.check('connect')
    def login(self, user, password): self.check('login')
    def sendcmd(self, command):
        assert command == 'NOOP'
        self.check('noop')
        return '200 OK'

namespace['DeadlineFTP'] = FTP
old = {name: os.environ.get(name) for name in ['XWN_EMULATOR_FTP_USER', 'XWN_EMULATOR_FTP_PASSWORD']}
try:
    os.environ['XWN_EMULATOR_FTP_USER'] = 'test'
    os.environ['XWN_EMULATOR_FTP_PASSWORD'] = 'test'
    for stage in ['connect', 'login', 'noop']:
        clock.value = 0; FTP.attempts = FTP.closes = 0
        FTP.fail_stage = stage; FTP.fail_count = 3
        result = namespace['wait_dashboard'](1)
        assert result['attempts'] == FTP.attempts == FTP.closes == 4
        assert not result['physical_access'] and clock.value <= 1
        checks += 3
    clock.value = 0; FTP.attempts = FTP.closes = 0
    FTP.fail_count = 100; FTP.fail_stage = 'connect'
    try: namespace['wait_dashboard'](.5)
    except (ftplib.error_temp, AssertionError): pass
    else: raise AssertionError('deadline failed to close')
    assert clock.value <= .5 and FTP.attempts == FTP.closes and FTP.attempts <= 4
    checks += 3
finally:
    for name, value in old.items():
        if value is None: os.environ.pop(name, None)
        else: os.environ[name] = value

trace = source.read_text()
assert "if ask('qqemu.PhyMemMode')!='0':quarantined=True" in trace
assert "Qqemu.PhyMemMode:1" not in trace and "prior_physical_mode']=='0'" in trace
assert "ask('qqemu.PhyMemMode')" in trace and "ask('qemu.PhyMemMode')" not in trace
stub=(k/'source/gdbstub/gdbstub.c').read_text(); system=(k/'source/gdbstub/system.c').read_text()
assert '.cmd = "qemu.PhyMemMode"' in stub
assert '.cmd = "qemu.PhyMemMode:"' in stub
assert 'case \'q\':' in stub and 'case \'Q\':' in stub
assert 'handle_gen_query' in stub and 'handle_gen_set' in stub
assert 'phy_memory_mode = 0;' in system and 'phy_memory_mode = 1;' in system
checks += 7
dest.write_text(json.dumps(dict(passed=True, checks=checks,
    utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
    test_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    scope='Actual helper source with failure adapters; not guest or backend qualification',
    physical_access=False), indent=2) + '\n')
print('Guard helper checks:', checks)
