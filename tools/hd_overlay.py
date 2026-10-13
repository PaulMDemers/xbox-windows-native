"""Verified six-file HD deployment, with immutable local preimages and no boot API."""
import hashlib
import json
import os
import time
import zipfile
from pathlib import Path

PATHS = (
    '/F/winnt/system32/xwnown.dll',
    '/F/winnt/system32/drivers/xboxvnt5.sys',
    '/E/Applications/XWNFBoot/loader/xboxbvid.dll',
    '/E/Applications/XWNFBoot/rosload.exe',
    '/E/Applications/XWNFBoot/freeldr.sys',
    '/E/Applications/XWNFBoot/default.xbe',  # Launcher always last; not multi-file atomicity.
)
PROFILES = ('baseline-restore', '720p', '1080i')
ARCHIVE_SHA = '474957aa6d2eb4cd8c3818a26ad0568e4b9c104b8159891c065b1491c8f6930d'


class Refused(RuntimeError):
    pass


def require(value, message):
    if not value:
        raise Refused(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def info(data):
    return {'bytes': len(data), 'sha256': sha(data)}


def save(path, value):
    """Bounded sharing-error retry; never truncate an existing journal in place."""
    path = Path(path)
    temp = path.with_suffix('.tmp')
    data = (json.dumps(value, indent=2) + '\n').encode('utf-8')
    with temp.open('wb') as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    for attempt in range(40):
        try:
            os.replace(temp, path)
            return
        except PermissionError:
            if attempt == 39:
                raise
            time.sleep(.05)


def exclusive_bytes(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    require(path.read_bytes() == data, 'Local backup readback mismatch')


class Package:
    def __init__(self, archive, policy):
        archive, policy = Path(archive), Path(policy)
        raw = archive.read_bytes()
        require(sha(raw) == ARCHIVE_SHA, 'Not the immutable 0.2.0 overlay')
        self.policy = load(policy)
        require(self.policy['overlay_sha256'] == ARCHIVE_SHA, 'Policy/archive mismatch')
        with zipfile.ZipFile(archive) as z:
            require(len(z.infolist()) == 23 and len(set(z.namelist())) == 23, 'Duplicate or missing entries')
            manifest = json.loads(z.read('MANIFEST.json'))
            expected = {mode + path for mode in PROFILES for path in PATHS}
            require(set(manifest['files']) == expected, 'Unexpected payload paths')
            self.profiles = {}
            for mode in PROFILES:
                self.profiles[mode] = {}
                for path in PATHS:
                    data = z.read(mode + path)
                    require(info(data) == manifest['files'][mode + path], 'Payload hash mismatch')
                    self.profiles[mode][path] = data
        self.baseline = self.policy['baseline_files']
        require(set(PATHS) <= set(self.baseline), 'Incomplete baseline')
        require(len(self.baseline) == 26, 'Wrong protected inventory')
        for path in PATHS:
            require(info(self.profiles['baseline-restore'][path]) == self.baseline[path], 'Wrong baseline payload')
        self.pins = {str(archive.resolve()): ARCHIVE_SHA,
                     str(policy.resolve()): sha(policy.read_bytes()),
                     str(Path(__file__).resolve()): sha(Path(__file__).read_bytes())}
        cli = Path(__file__).with_name('deploy-hd.py')
        self.pins[str(cli.resolve())] = sha(cli.read_bytes())

    def verify_pins(self, pins):
        require(pins == self.pins, 'Attempt belongs to different inputs')
        for path, digest in pins.items():
            require(sha(Path(path).read_bytes()) == digest, 'Frozen input changed')

    def read_all(self, remote):
        return {path: remote.get(path) for path in self.baseline}

    def identify(self, data):
        for path, expected in self.baseline.items():
            if path not in PATHS:
                require(info(data[path]) == expected, 'Protected prerequisite differs: ' + path)
        matches = [mode for mode in PROFILES if all(data[p] == self.profiles[mode][p] for p in PATHS)]
        require(len(matches) == 1, 'Unrecognized or mixed installed profile')
        return matches[0]


def prepare(remote, package, directory, profile):
    require(profile in PROFILES, 'Unknown profile')
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    journal = directory / 'transaction.json'
    record = {'version': 1, 'state': 'preparing', 'target_profile': profile,
              'pins': package.pins, 'writes': [], 'restore_writes': [],
              'launch_requested': False, 'scope': 'Six-file overlay only; no boot/full restore'}
    save(journal, record)
    try:
        data = package.read_all(remote)
        record['incoming_profile'] = package.identify(data)
        record['before'] = {path: info(value) for path, value in data.items()}
        for path, value in data.items():
            exclusive_bytes(directory / 'before' / path.lstrip('/'), value)
        # A second complete read ensures the captured profile did not change mid-plan.
        require(package.read_all(remote) == data, 'Console changed during capture')
        record['state'] = 'prepared'
        save(journal, record)
    except BaseException as exc:
        record.update(state='prepare_failed', error_type=type(exc).__name__)
        save(journal, record)
        raise
    return record


def open_attempt(package, directory):
    directory = Path(directory)
    journal = directory / 'transaction.json'
    record = load(journal)
    require(record['version'] == 1, 'Unknown journal')
    package.verify_pins(record['pins'])
    require(record['target_profile'] in PROFILES and record['incoming_profile'] in PROFILES, 'Invalid profile')
    require(set(record['before']) == set(package.baseline), 'Incomplete preimage inventory')
    require(record['launch_requested'] is False, 'Unexpected launch state')
    before = {}
    for path in package.baseline:
        data = (directory / 'before' / path.lstrip('/')).read_bytes()
        require(info(data) == record['before'][path], 'Backup changed: ' + path)
        before[path] = data
    require(package.identify(before) == record['incoming_profile'], 'Invalid preimage profile')
    for field in ['writes', 'restore_writes']:
        require(all(p in PATHS for p in record[field]), 'Unexpected journal write path')
    return journal, record, before


def apply(remote, package, directory):
    journal, record, before = open_attempt(package, directory)
    require(record['state'] == 'prepared', 'Apply is one-shot; inspect or restore this attempt')
    target = dict(before)
    target.update(package.profiles[record['target_profile']])
    try:
        require(package.read_all(remote) == before, 'Console changed since prepare')
        record['state'] = 'applying'
        save(journal, record)
        for path in PATHS:
            if target[path] == before[path]:
                continue
            require(remote.get(path) == before[path], 'Write preimage changed')
            record['writes'].append(path)  # Intent is durable BEFORE any remote write.
            save(journal, record)
            remote.put(path, target[path])
            require(remote.get(path) == target[path], 'Write readback mismatch')
        actual = package.read_all(remote)
        require(actual == target, 'Final payload/protected inventory differs')
        record.update(state='committed', after={p: info(v) for p, v in actual.items()})
        save(journal, record)
    except BaseException as exc:
        record.update(state='quarantined', error_type=type(exc).__name__, do_not_boot=True)
        save(journal, record)
        raise
    return record


def restore(remote, package, directory):
    journal, record, before = open_attempt(package, directory)
    require(record['state'] in ('applying', 'committed', 'quarantined', 'restoring', 'restored'), 'No restorable transaction')
    target = dict(before)
    target.update(package.profiles[record['target_profile']])
    try:
        current = package.read_all(remote)
        # Only the recorded original and intended bytes are owned recovery states.
        # Partial/foreign writes are preserved and refused, never silently overwritten.
        for path, value in current.items():
            allowed = (before[path], target[path]) if path in record['writes'] else (before[path],)
            if value not in allowed:
                capture = Path(directory) / 'unknown' / sha(value)
                if not capture.exists():
                    exclusive_bytes(capture, value)
                record['unknown_file'] = {'path': path, **info(value)}
                raise Refused('Unknown or partial file; preserved, manual recovery review required')
        record['state'] = 'restoring'
        save(journal, record)
        for path in PATHS:
            if current[path] == before[path]:
                continue
            require(remote.get(path) == current[path], 'Restore preimage changed')
            record['restore_writes'].append(path)
            save(journal, record)
            remote.put(path, before[path])
            require(remote.get(path) == before[path], 'Restore readback mismatch')
        actual = package.read_all(remote)
        require(actual == before, 'Full original inventory not restored')
        record.update(state='restored', restored={p: info(v) for p, v in actual.items()}, do_not_boot=False)
        save(journal, record)
    except BaseException as exc:
        record.update(state='quarantined', error_type=type(exc).__name__, do_not_boot=True)
        save(journal, record)
        raise
    return record
