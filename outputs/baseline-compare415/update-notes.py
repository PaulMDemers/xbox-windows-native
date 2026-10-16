"""Prepend current findings without rewriting historical continuation bytes."""
from pathlib import Path
W=Path(__file__).resolve().parents[2]
prefix='''# 415 closed: working demo versus clean rebuild, no physical mutation

User approved comparing the working demo against the clean rebuild. This
supersedes the older next-step early-Cromwell tracing plan. Do not describe the
failure as intermittent: same-build/same-route/same-start-state randomness has
not been established. Successful direct File Explorer and failed menu/FTP
observations used the same installed demo files. Fresh403/405/406 binaries have
not been installed over that demo; no newer-binary physical regression proved.

415 one read-only FTP capture:31 E files, all protected411 code/startup exact.
34 files extracted from CLOSED406 disk, disk SHA unchanged and original cold
inventory exact.65 private captures rehashed,21 analysis/source inputs pinned.
No console C access, physical writes/launches, builds or guest experiments.
All owned commands closed; read-only process query found no xemu process.

Launcher differs only one displayed-date byte plus20 valid section digest bytes;
wrapper/Cromwell text exact. Six project drivers differ only timestamps/checksum.
16 selected Microsoft system/player files exact. HAL/FreeLoader/ROS loader have
nonmetadata differences: build-source strings explain SOME differences, not
complete equivalence. Linear FreeLoader disassembly includes data:2153 unknown
spans are not2153 proven instruction changes.74 actual binary mutation controls
pass, including digest-valid changed XBE code refusal. No runtime equivalence
or failure-cause claim. See baseline-compare415 REPORT/DESIGN/NEXT/final-review.

Selected registry comparison: fresh HidServ registration absent (exe/INF exist),
AutoReboot1 vs demo0, six ImagePath text-identical type differences; stored video
defaults differ but do not establish effective mode. Demo was observed720p.
Fresh freeldr.ini omits demo MinimalUI=Yes, and fresh lacks marker-gated outline
startup helper. No configuration automatically changed. libhivex loader failure
before hive open preserved; exact reader succeeded with process-local lib path.

Next resolve actual remaining loader build differences from pinned source and
compiler records, prepare separate candidate with matched configuration, then
use SAME direct File Explorer route/start-state for a physical comparison.
Do not substitute FTP SITE and call it the same route. Do not replace the whole
demo or waive six FATX long-name exclusions/strict-event clean-install blockers.
Demo path E:/Applications/XWNEBoot/default.xbe; clip C:/xwndemo407/play.cmd.
E720p/FATX390/video303/audio004 and F rollback unchanged, no public tag.
No hardware action queued. C24707448832/E21598044160 bytes at final read-only
capacity check; preserve projected20GiB guard and all backing chains.

'''.encode('utf-8')
for name in ['CONTINUATION.md','STATUS.md']:
    path=W/'outputs/engineering-notes'/name
    prior=path.read_bytes()
    assert not prior.startswith(b'# 415 closed:')
    path.write_bytes(prefix+prior)
    assert path.read_bytes()[len(prefix):]==prior
