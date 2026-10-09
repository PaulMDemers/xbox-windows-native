"""Preserve exact source-byte mismatch in uncompiled first build; no mutation."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;old=k/'build001-expected';src=Path('/home/paul/xbox-windows-native/build/video-body-timing170-001/source/win32ss/drivers/displays/framebuf')
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();dest=k/'build001-integrity-failure.json';assert not dest.exists()
review=read(old/'source-review.json');report=read(old/'build-report.json');assert report['status']=='failed' and not report['builds']
rows=[]
for name,digest in review['source_files'].items():
 expected=old/'display'/name;actual=src/name;assert sha(expected)==digest
 if sha(actual)!=digest:
  rows.append(dict(file=name,expected_sha256=digest,actual_sha256=sha(actual),normalized_bytes_equal=expected.read_bytes().replace(b'\r\n',b'\n')==actual.read_bytes()))
assert sorted(v['file'] for v in rows)==['CMakeLists.txt','framebuf.h','ownership.c'] and all(v['normalized_bytes_equal'] for v in rows)
r=dict(source_integrity_passed=False,compiled=False,guest_launched=False,physical_access=False,mismatches=rows,
 failure='Host Windows text append produced mixed line endings; unified patch reproduces LF source only. Source hash guard stopped before compilation.',
 failed_build_report_sha256=sha(old/'build-report.json'),failed_patch_sha256=sha(old/'0113-body-timing.patch'),failed_driver_build_source_sha256=sha(old/'build.py'),
 host_clang_attempt='host-tests001.py: unavailable clang, no executable created; GCC ASan/UBSan tested identical actual header4142checks successfully.',
 corrected_build='fresh170-002 with normalized reviewed LF sources; source hashes exact before compile; all failed inputs retained')
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(rows))
