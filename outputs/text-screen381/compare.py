"""One physical 720p visual comparison; unchanged E demo, no test autorun."""
import importlib.util, json, sys
from pathlib import Path

K = Path(__file__).resolve().parent
W = K.parents[1]
sys.path.insert(0, str(K.parent/'demo-audio-level256'))
from common001 import connect, get, sha, utc
sys.path.insert(0, str(K.parent/'surface-bridge260'))
from atomic_json import write_json
s = importlib.util.spec_from_file_location('selector', W/'tools/configure-e-display.py')
selector = importlib.util.module_from_spec(s); s.loader.exec_module(selector)
POLICY = W/'tools/e-display-policy.json'
RECEIPT = Path('E:/xwn381/mode720p001')
LAUNCHER = Path('E:/xwn374/build001/default.xbe')
START = '/E/documents and settings/all users/start menu/programs/startup/xwnsetup.cmd'
START_HASH = 'da47fdf32e29b81ba9f5148d86f291ed708c9432c268b1682668c5b50883aa43'

def apply():
    dest = K/'mode720p001.json'; assert not dest.exists() and not RECEIPT.exists()
    policy = selector.read_json(POLICY)
    with connect() as f:
        assert selector.inspect(f, policy)[0] == '1080i'
        assert sha(get(f, START)) == START_HASH
        audio = get(f, '/E/winnt/system32/drivers/xwnaci207.sys')
        fatx = get(f, '/E/winnt/system32/drivers/xwnfatx.sys')
        r = dict(utc=utc(), policy_sha256=sha(POLICY.read_bytes()),
                 script_sha256=sha(Path(__file__).read_bytes()),
                 selector_sha256=sha((W/'tools/configure-e-display.py').read_bytes()),
                 startup_sha256=START_HASH, audio_sha256=sha(audio), fatx_sha256=sha(fatx),
                 console_C_accessed=False, drivers_changed=False)
        r['result'] = selector.apply(f, policy, '720p', LAUNCHER.read_bytes(), RECEIPT)
        assert get(f, '/E/winnt/system32/drivers/xwnaci207.sys') == audio
        assert get(f, '/E/winnt/system32/drivers/xwnfatx.sys') == fatx
        assert sha(get(f, START)) == START_HASH
        write_json(dest, r)
    print(json.dumps(r, indent=2))

def launch():
    dest = K/'launch720p001.json'; assert not dest.exists()
    assert selector.read_json(K/'mode720p001.json')['result']['mode'] == '720p'
    with connect() as f:
        assert selector.inspect(f, selector.read_json(POLICY))[0] == '720p'
        assert sha(get(f, START)) == START_HASH
        r = dict(requested=True, utc=utc(), mode='720p', stay_at_desktop=True,
                 command=r'SITE EXEC E:\Applications\XWNEBoot\default.xbe',
                 console_C_accessed=False, repeat_forbidden=True)
        write_json(dest, r)
        f.sock.settimeout(20)
        try: r['reply'] = f.sendcmd(r['command'])
        except Exception as e: r['reply_uncertain'] = type(e).__name__
        write_json(dest, r)
    print(json.dumps(r, indent=2))

if __name__ == '__main__':
    assert sys.argv[1:] in [['apply'], ['launch']]
    globals()[sys.argv[1]]()
