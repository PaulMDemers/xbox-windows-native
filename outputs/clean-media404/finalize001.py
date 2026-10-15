"""Publish recorded media states after both cold PC audits; no guest operations."""
import hashlib, json
from pathlib import Path
from qualification002 import qualify
K = Path(__file__).resolve().parent
W = K.parents[1]
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
out = K / 'qualification001.json'
assert not out.exists()
inventory = read(K / 'media-inventory001.json')
structures = {r['id']: r for r in read(K / 'media-structure001.json')}
first, final = [read(K / ('cold-phase%02d.json' % p)) for p in [3, 4]]
probe = read(K / 'probe-build002.json')['binary_sha256']
result = qualify(first, final, structures['customized-sp4-oem-en']['kernel'], probe)
phases = [read(K / ('oem001-phase%02d.json' % p)) for p in range(1, 5)]
result['all_phases_closed_without_timeout'] = all(r['closed'] and r['exit_code'] == 0 and not r['deadline'] for r in phases)
result['actual_disk_only_command'] = phases[-1]['disk_only'] and not any('media=cdrom' in s or 'if=floppy' in s for s in phases[-1]['command'])
assert result['all_phases_closed_without_timeout'] and result['actual_disk_only_command']
result['cold_audits_sha256'] = {p.name: sha(p) for p in [K / 'cold-phase03.json', K / 'cold-phase04.json']}
out.write_text(json.dumps(result, indent=2) + '\n')
media = []
for row in inventory:
    r = {k: row[k] for k in ['id', 'filename', 'bytes', 'sha256', 'sha1', 'setup_channel']}
    label = 'retail' if row['id'].startswith('retail') else 'customized'
    online = read(K / ('online-' + label + '001.json'))
    assert online['status'] == 'full_download_readback_exact_match' and online['sha256'] == row['sha256']
    s = structures[row['id']]
    r.update(volume_label=s['volume_id'], kernel=s['kernel'],
             source='User-supplied disc; independent full online download matches',
             original_microsoft_authenticity_proven=False,
             online_comparison=dict(url=online['url'], checked_date='2026-10-15',
                                    complete_download_and_readback_match=True))
    validation = dict(iso_file_read_passed=True, iso_file_count=s['iso_files'],
                      selected_cabinet_decompression_passed=all(v['complete_decompression_passed'] for v in s['archives']),
                      clean_pc_install_scoped_passed=False, strict_clean_pc_passed=False,
                      fresh_xbox_assembly_qualified=False, physical_qualified=False)
    if label == 'customized':
        validation.update(status='clean_pc_install_scoped_pass' if result['clean_pc_install_scoped_passed'] else 'clean_pc_install_failed',
                          clean_pc_install_scoped_passed=result['clean_pc_install_scoped_passed'],
                          strict_clean_pc_passed=result['strict_clean_pc_passed'],
                          strict_events_passed=result['strict_events_passed'],
                          typed_decode_complete=result['typed_decode_complete'],
                          automatic_runonce_handoff_passed=False,
                          disk_only_witness_invocation=result['disk_only_witness_invocation'],
                          typed_decode_errors=[e for h in final['hives'] for e in h['typed_decode_errors']],
                          media_detached_boot_passed=result['gates']['disk_only_logon'],
                          five_hives_parsed_clean=result['gates']['final_structure'],
                          normal_shutdown_events=final['normal_shutdown_events'],
                          warnings_errors=final['warnings_errors'],
                          evidence_id='clean-media404/oem001', checked_date='2026-10-15',
                          qualification_record_sha256=sha(out),
                          configuration='Blank 2 GiB PC disk; 64 MiB Pentium III/IDE/Cirrus; no network; OemPreinstall=No; private first-logon witness')
    else:
        validation.update(status='integrity_verified_install_pending_matching_retail_key',
                          installation_blocker='Matching retail product key not supplied; OEM key is not interchangeable')
    r['validation'] = validation; media.append(r)
manifest = dict(schema=1, scope='Exact disc byte identities and recorded test scopes; recognition is not installation success, authenticity or a license grant', media=media)
with (W / 'upstream/windows-media.json').open('x', encoding='utf-8') as f:
    json.dump(manifest, f, indent=2); f.write('\n')
print(json.dumps(result, indent=2))
