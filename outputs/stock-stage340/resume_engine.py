"""Continue only a closed, journaled create-only stage; never overwrite a file."""
from engine import ROOTS, LAUNCHER, allowed, digest

def validate_journal(rows, files, directories):
    done_dirs, pending_dirs, verified, intended = set(), set(), set(), set()
    for row in rows:
        p, kind = row['path'], row['kind']
        assert allowed(p)
        if kind == 'mkdir_intent':
            assert p in directories and p not in pending_dirs
            pending_dirs.add(p)
        elif kind == 'mkdir_done':
            assert p in pending_dirs and p not in done_dirs
            done_dirs.add(p)
        elif kind == 'write_intent':
            assert p in files and p not in intended and row['meta'] == files[p]
            intended.add(p)
        elif kind == 'write_verified':
            assert p in intended and p not in verified and row['meta'] == files[p]
            verified.add(p)
        else:
            raise AssertionError('Unknown journal record')
    assert done_dirs == pending_dirs == directories
    assert LAUNCHER not in intended, 'A previously attempted launcher needs separate review'
    assert len(intended - verified) <= 1
    ordered = sorted(set(files) - {LAUNCHER})
    assert intended == set(ordered[:len(intended)])
    assert verified == set(ordered[:len(verified)])
    return intended, verified

def resume(files, directories, rows, read_local, remote, journal):
    assert LAUNCHER in files and all(allowed(p) for p in files)
    assert all(allowed(p) for p in directories)
    assert len({p.lower() for p in files}) == len(files)
    intended, verified = validate_journal(rows, files, directories)
    for p, meta in files.items():
        b = read_local(p)
        assert len(b) == meta['bytes'] and digest(b) == meta['sha256'], p
    # Full owned-root inventory rejects foreign paths, missing completed files,
    # directory substitutions and a prematurely present launcher before any write.
    actual_dirs, actual_files = remote.inventory(ROOTS)
    assert actual_dirs == directories
    assert verified <= actual_files <= intended
    assert LAUNCHER not in actual_files
    for p in sorted(actual_files):
        assert remote.read(p) == read_local(p), 'Existing file mismatch: ' + p
        journal('existing_verified', p, files[p])
    count = len(actual_files)
    for p in sorted(set(files) - actual_files - {LAUNCHER}) + [LAUNCHER]:
        assert not remote.exists(p), 'Unexpected new path: ' + p
        b = read_local(p)
        assert len(b) == files[p]['bytes'] and digest(b) == files[p]['sha256']
        journal('write_intent', p, files[p])
        remote.create(p, b)
        assert remote.read(p) == b, 'Readback mismatch: ' + p
        journal('write_verified', p, files[p])
        count += 1
    return dict(complete=True, files=count, existing_files=len(actual_files),
                created_files=count-len(actual_files), launcher_written_last=True,
                readback_verified=True, overwritten_files=0)
