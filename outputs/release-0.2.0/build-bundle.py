"""One-shot private packaging of existing verified artifacts; no deployment/build."""
import hashlib
import json
import subprocess
import zipfile
from pathlib import Path

KIT = Path(__file__).resolve().parent
WS = KIT.parents[1]
OUT = Path('D:/Codex-archive/xbox-windows-native/0.2.0')


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_hash(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def encoded(obj):
    return (json.dumps(obj, indent=2) + '\n').encode('utf-8')


def row(path):
    return {'path': str(path), 'bytes': path.stat().st_size, 'sha256': file_hash(path)}


def make_zip(path, items):
    """Items are immutable bytes or pre-hashed file paths. Rehash all readback."""
    expected = {}
    with zipfile.ZipFile(path, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
        for name, value in sorted(items.items()):
            assert name and not name.startswith('/') and '..' not in Path(name).parts
            if isinstance(value, Path):
                expected[name] = {'bytes': value.stat().st_size, 'sha256': file_hash(value)}
                archive.write(value, name, compress_type=zipfile.ZIP_STORED)
            else:
                expected[name] = {'bytes': len(value), 'sha256': digest(value)}
                info = zipfile.ZipInfo(name, date_time=(2026, 10, 12, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                archive.writestr(info, value)
    with zipfile.ZipFile(path) as archive:
        assert len(archive.infolist()) == len(expected)
        assert set(archive.namelist()) == set(expected)
        for name, info in expected.items():
            assert archive.getinfo(name).file_size == info['bytes']
            with archive.open(name) as stream:
                assert hashlib.file_digest(stream, 'sha256').hexdigest() == info['sha256']
    return {**row(path), 'entries': expected, 'all_entries_readback_verified': True}


def main():
    assert not OUT.exists() and not (KIT / 'bundle.json').exists(), 'Consumed output ID'
    stage = read(WS / 'outputs/release-staging325/bundle.json')
    source = Path(stage['path'])
    assert source.stat().st_size == stage['bytes'] and file_hash(source) == stage['sha256']
    before = read(WS / 'outputs/hd-physical324/final-review.json')
    low = read(WS / 'outputs/hd-observed315/final-review.json')
    assert before['scoped_passed'] and before['integrity_passed']
    assert low['scoped_passed'] and low['integrity_passed']
    assert before['normal_shutdown_count'] == 1 and all(before['restored_payloads'].values())
    assert before['strict_passed'] is False and before['release_qualified'] is False
    observation = read(KIT / 'user-observation.json')
    assert observation['quote'] == 'The video output had looked normal at 1080'
    assert observation['normal_picture_user_reported'] is True
    payload = {}
    with zipfile.ZipFile(source) as archive:
        assert len(archive.infolist()) == stage['entries'] == 21
        for name, info in stage['manifest']['files'].items():
            data = archive.read(name)
            assert len(data) == info['bytes'] and digest(data) == info['sha256']
            payload[name] = data
    assert len(payload) == 18
    evidence = {}
    for relative in ['outputs/hd-observed315/final-review.json',
                     'outputs/hd-physical324/final-review.json',
                     'outputs/hd-physical324/user-observation.json',
                     'outputs/release-staging325/bundle.json',
                     'outputs/demo-audio-level256/capture-summary.json']:
        evidence[relative] = file_hash(WS / relative)
    recovery = read(WS / 'outputs/demo-audio-level256/capture-summary.json')
    recovery_files = {}
    for info in recovery['bundles']:
        path = Path(info['path'])
        assert path.stat().st_size == info['bytes'] and file_hash(path) == info['sha256']
        recovery_files['recovery/' + path.name] = path
    recovery_manifest = Path(recovery['manifest_path'])
    assert file_hash(recovery_manifest) == recovery['manifest_sha256']
    recovery_files['recovery/capture-manifest.json'] = recovery_manifest
    qualification = {
        'release': '0.2.0', 'designation': 'private experimental HD release',
        'release_scope_accepted': True, 'strict_passed': False,
        'known_Ftdisk49_retained': stage['qualification']['known_Ftdisk49_retained'],
        'physical720p_workload_passed': True, 'physical1080i_workload_passed': True,
        'physical1080i_user_observation': observation,
        'original_closed_machine_verdicts_unchanged': True,
        'tv_osd_mode_independently_confirmed': False,
        'repeat_boot_reliability_established': False,
        'gpu_acceleration': False, 'runtime_mode_switching': False,
        'full_restore_tested': False, 'whole_disk_backup': False,
        'new_system_capture': False, 'new_compiler_rebuild': False,
        'physical_deployment_during_packaging': False,
        'console_baseline_restored': True,
        'historical_WAVE_MAPPER_ID_failure_retained': True,
        'exact_stereo_routing_confirmed': False,
    }
    assert qualification['known_Ftdisk49_retained'] is True
    manifest = {
        'release': '0.2.0', 'intended_immutable_source_tag': 'v0.2.0',
        'packaging_parent_commit': subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'], cwd=WS, text=True).strip(),
        'source_tag_receipt': 'source-evidence-bundles.json is generated after tagging',
        'packaging_source_sha256': {p.name: file_hash(p) for p in
                                    [Path(__file__), KIT / 'README.md', KIT / 'USAGE.md', KIT / 'user-observation.json']},
        'files': stage['manifest']['files'],
        'installed_prerequisite_files': stage['manifest']['installed_prerequisite_files'],
        'unchanged_staging_archive': row(source),
        'evidence_sha256': evidence,
        'historical_recovery_archives': recovery['bundles'],
        'recovery_manifest_sha256': recovery['manifest_sha256'],
        'recovery_exclusions': recovery['exclusions'],
        'target': 'Tested Conexant HDTV demo; upgrade overlay, not universal or bare-metal installer',
    }
    docs = {name: (KIT / name).read_bytes() for name in ['README.md', 'USAGE.md', 'user-observation.json']}
    docs['MANIFEST.json'] = encoded(manifest)
    docs['QUALIFICATION.json'] = encoded(qualification)
    OUT.mkdir(parents=True)
    overlay = make_zip(OUT / 'xwn-0.2.0-hd-overlay.zip', {**payload, **docs})
    full = make_zip(OUT / 'xwn-0.2.0-private-demo.zip', {
        **docs, **recovery_files,
        'xwn-0.2.0-hd-overlay.zip': Path(overlay['path']),
        'recovery/capture-summary.json': WS / 'outputs/demo-audio-level256/capture-summary.json',
    })
    # Revalidate all inputs after copying; old release evidence is never rewritten.
    assert file_hash(source) == stage['sha256']
    for relative, expected in evidence.items():
        assert file_hash(WS / relative) == expected
    for info in recovery['bundles']:
        assert file_hash(Path(info['path'])) == info['sha256']
    result = {'completed': True, 'release': '0.2.0', 'archives': [overlay, full],
              'manifest': manifest, 'qualification': qualification,
              'tagging_is_separate_step': True, 'physical_access': False}
    for name, data in docs.items():
        (OUT / name).write_bytes(data)
    for destination in [KIT / 'bundle.json', OUT / 'bundle.json']:
        destination.write_bytes(encoded(result))
    (OUT / 'SHA256SUMS.txt').write_text(''.join(
        f"{info['sha256']}  {Path(info['path']).name}\n" for info in [overlay, full]), encoding='ascii')
    print(json.dumps({'archives': [{key: info[key] for key in ['path', 'bytes', 'sha256']} for info in [overlay, full]],
                      'verified_entries': [len(overlay['entries']), len(full['entries'])]}, indent=2))


if __name__ == '__main__':
    main()
