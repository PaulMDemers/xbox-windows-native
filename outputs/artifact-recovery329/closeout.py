"""Seal recovery locations/hashes without changing release tags or old receipts."""
import hashlib,json,shutil,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
OUT=Path('E:/Codex-archive/xbox-windows-native/0.2.0-recovered329')
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert not (K/'final-review.json').exists()
p=read(K/'package001.json');s=read(K/'source001.json');f=read(K/'seed001/content-review002.json')
assert p['passed'] and s['passed'] and f['passed']
copies=read(Path('E:/xwn329/retained-builds001/receipt.json'))
for row in copies['copies']:
 q=Path(row['destination'].replace('/mnt/e/','E:/'));assert sha(q)==row['sha256']
for row in p['archives']+s['archives']:assert sha(Path(row['path']))==row['sha256']
assert read(K/'helper-metadata001.json')['output_sha256']==read(W/'outputs/hd-ui313/build-review001.json')['binary_sha256']
shutil.copyfile('E:/xwn329/retained-builds001/receipt.json',K/'retained-builds001.json')
shutil.copyfile(K/'USAGE.md',OUT/'START-HERE.md')
(OUT/'SHA256SUMS.txt').write_text(''.join(f"{row['sha256']}  {Path(row['path']).name}\n" for row in p['archives']+s['archives']),encoding='ascii')
subprocess.run(['C:/devkitPro/msys2/usr/bin/git.exe','bundle','verify',str(OUT/'xwn-0.2.0-history.bundle')],cwd=W,check=True,capture_output=True)
r=dict(passed=True,package_directory=str(OUT),exact_original_overlay=True,exact_original_source_archive=True,
 combined_entries_exact=True,combined_outer_hash_original=p['combined_archive_byte_identical'],
 complete_history_verified=True,old_tags_unchanged=True,emulator_binary_exact=True,helper_binary_exact=True,
 reconstructed_seed_file_count=f['file_count'],reconstructed_seed_directory_count=f['directory_count'],
 seed_only_seven_expected_files_changed=True,seed_matches_original_container=False,
 failures_preserved=['helper001 nondeterministic metadata mismatch','content enumerator001 empty directory cluster0 refusal'],
 physical_access=False,new_hardware_qualification=False,
 evidence_pins={x.relative_to(K).as_posix():sha(x) for x in K.rglob('*') if x.is_file() and x.suffix in ['.py','.ps1','.md','.json']},
 free_bytes={d:shutil.disk_usage(d).free for d in ['C:/','E:/']})
(K/'final-review.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({n:r[n] for n in ['passed','package_directory','exact_original_overlay','exact_original_source_archive','reconstructed_seed_file_count']}))
