"""Archive the immutable private release tag; validate every Git blob and bundle."""
import hashlib
import json
import subprocess
import zipfile
from pathlib import Path

KIT = Path(__file__).resolve().parent
WS = KIT.parents[1]
OUT = Path('D:/Codex-archive/xbox-windows-native/0.2.0')
TAG = 'v0.2.0'
GIT = 'C:/Program Files/Git/cmd/git.exe'


def git(*args):
    return subprocess.check_output([GIT, *args], cwd=WS)


def record(path):
    with path.open('rb') as stream:
        sha = hashlib.file_digest(stream, 'sha256').hexdigest()
    return {'path': str(path), 'bytes': path.stat().st_size, 'sha256': sha}


def main():
    source = OUT / 'xwn-0.2.0-source-evidence.zip'
    history = OUT / 'xwn-0.2.0-history.bundle'
    assert OUT.is_dir() and not source.exists() and not history.exists()
    assert not (KIT / 'source-evidence-bundles.json').exists(), 'Consumed output ID'
    revision = git('rev-list', '-n', '1', TAG).decode().strip()
    tag_object = git('rev-parse', TAG).decode().strip()
    previous_tag = git('rev-parse', 'v0.1.0').decode().strip()
    previous_commit = git('rev-list', '-n', '1', 'v0.1.0').decode().strip()
    assert revision == git('rev-parse', 'HEAD').decode().strip()
    assert not git('status', '--porcelain', '--untracked-files=no')
    assert git('rev-parse', '--show-object-format').decode().strip() == 'sha1'
    git('archive', '--format=zip', '--output=' + str(source), TAG)
    blobs = {}
    for entry in git('ls-tree', '-r', '-z', TAG).split(b'\0'):
        if not entry:
            continue
        metadata, name = entry.split(b'\t', 1)
        mode, kind, oid = metadata.split(b' ')
        assert kind == b'blob', 'Unexpected submodule or non-blob'
        blobs[name.decode('utf-8')] = oid.decode('ascii')
    with zipfile.ZipFile(source) as archive:
        entries = [item for item in archive.infolist() if not item.is_dir()]
        assert len(entries) == len(blobs) and {item.filename for item in entries} == set(blobs)
        for item in entries:
            data = archive.read(item.filename)
            actual = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
            assert actual == blobs[item.filename], item.filename
    git('bundle', 'create', str(history), 'refs/tags/v0.2.0', 'refs/tags/v0.1.0')
    verify = subprocess.run([GIT, 'bundle', 'verify', str(history)], cwd=WS,
                            capture_output=True, text=True, check=True)
    heads = git('bundle', 'list-heads', str(history)).decode()
    assert f'{tag_object} refs/tags/v0.2.0' in heads
    assert f'{previous_tag} refs/tags/v0.1.0' in heads
    assert git('rev-parse', 'v0.1.0').decode().strip() == previous_tag
    result = {
        'tag': TAG, 'tag_object': tag_object, 'revision': revision,
        'source_entries_verified_against_git_blobs': len(blobs),
        'complete_history_bundle_verified': True, 'bundle_heads': heads.splitlines(),
        'bundle_verification': (verify.stdout + verify.stderr).strip(),
        'immutable_v0_1_0_tag_object': previous_tag,
        'immutable_v0_1_0_revision': previous_commit,
        'archives': [record(source), record(history)],
        'private_only': True, 'public_history_audit_complete': False,
        'physical_access': False,
    }
    data = (json.dumps(result, indent=2) + '\n').encode('utf-8')
    (KIT / 'source-evidence-bundles.json').write_bytes(data)
    (OUT / 'source-evidence-bundles.json').write_bytes(data)
    with (OUT / 'SHA256SUMS.txt').open('a', encoding='ascii', newline='\n') as stream:
        for info in result['archives']:
            stream.write(f"{info['sha256']}  {Path(info['path']).name}\n")
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
