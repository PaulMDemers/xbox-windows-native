"""Narrow UnleashX menu repair. Requires explicit exception for dashboard C."""
import json, sys, xml.etree.ElementTree as ET
from pathlib import Path

K = Path(__file__).resolve().parent
W = K.parents[1]
sys.path.insert(0, str(K.parent / 'demo-audio-level256'))
from common001 import connect, get, put, sha, utc
sys.path.insert(0, str(K.parent / 'surface-bridge260'))
from atomic_json import write_json

CONFIG = '/C/Dashboard/config.xml'
BACKUP = '/C/Dashboard/config.e380.bak'
TEMP = '/C/Dashboard/config.e380.new'
OLD = r'E:\Applications\XWNFBoot\default.xbe'
NEW = r'E:\Applications\XWNEBoot\default.xbe'

def patch(before):
    root = ET.fromstring(before.rstrip(b'\0'))
    menu = root.find('Menu')
    assert menu is not None
    items = [x for x in menu.findall('Item') if (x.text or '').strip() == 'Windows']
    assert len(items) == 1 and items[0].get('Action') == OLD
    token = b'Action="' + OLD.encode('ascii') + b'"'
    assert before.count(token) == 1
    after = before.replace(token, b'Action="' + NEW.encode('ascii') + b'"', 1)
    items[0].set('Action', NEW)
    assert ET.tostring(root) == ET.tostring(ET.fromstring(after.rstrip(b'\0')))
    assert after.replace(NEW.encode('ascii'), OLD.encode('ascii'), 1) == before
    return after

def install():
    assert sys.argv[1:] == ['install', '--authorized-menu-only-C-exception']
    dest = K / 'installed.json'
    local = Path('E:/xwn380/menu001')
    assert not dest.exists() and not local.exists()
    local.mkdir(parents=True)
    r = dict(started_utc=utc(), installed=False, config=CONFIG, backup=BACKUP,
             old_action=OLD, new_action=NEW, automatic_launch=False,
             C_exception='Only config.xml plus its unique backup/staging siblings',
             writes=[], renames=[])
    write_json(dest, r)
    with connect() as f:
        policy = json.loads((W/'tools/e-display-policy.json').read_text())
        for p, v in policy['prerequisites'].items():
            assert sha(get(f, p)) == v['sha256'], p
        target = get(f, policy['target'])
        assert sha(target) == policy['profiles']['1080i']['sha256']
        before = get(f, CONFIG)
        after = patch(before)
        for p in [BACKUP, TEMP]:
            assert get(f, p, optional=True) is None, 'Preserve existing '+p
        for name, data in [('before.xml', before), ('after.xml', after)]:
            q = local/name; q.write_bytes(data); assert q.read_bytes() == data
        r.update(before_sha256=sha(before), after_sha256=sha(after),
                 launcher_sha256=sha(target), private_backup=str(local/'before.xml'))
        r['writes'].append(TEMP); write_json(dest, r)
        put(f, TEMP, after)
        assert get(f, CONFIG) == before, 'Concurrent menu change'
        r['renames'].append([CONFIG, BACKUP]); write_json(dest, r)
        f.rename(CONFIG, BACKUP)
        try:
            r['renames'].append([TEMP, CONFIG]); write_json(dest, r)
            f.rename(TEMP, CONFIG)
        except Exception as e:
            r['error'] = repr(e)
            # Restore only if destination is absent; never overwrite an uncertain rename.
            if get(f, CONFIG, optional=True) is None:
                f.rename(BACKUP, CONFIG); r['restored_original'] = get(f, CONFIG) == before
            write_json(dest, r)
            raise
        assert get(f, CONFIG) == after and get(f, BACKUP) == before
        r.update(installed=True, readback_verified=True, completed_utc=utc(),
                 dashboard_reload_pending=True, menu_boot_observation_pending=True)
        write_json(dest, r)
    print(json.dumps(r, indent=2))

if __name__ == '__main__':
    install()
