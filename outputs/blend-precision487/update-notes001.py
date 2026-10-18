"""Prepend the exact closed state; preserve historical note bytes."""
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
text='''# Current: PC alpha precision characterized; Xbox487 closed without Windows results

Read outputs/d3d-blend484 REPORT/final-review (FAILED exact endpoints),
outputs/d3d-blend485 REPORT/draft-review (HELD, never built/launched),
outputs/blend-precision486 REPORT/DESIGN/final-review (PC arithmetic), and
outputs/blend-precision487 REPORT/DESIGN/NEXT/final-review plus actual records.
No next launch queued; dashboard back, temporary487 hook removed, normal
launcher/startup/protected720p unchanged. DashboardC untouched. Never rerun or
recollect484/486/487 runtimes; no executed-child parenting.

484 public MIT blend sample edf7b7c7...19611B, six captures per default/HEL process.
Both exited0 and PC restarted normally, but exact alpha0/255 endpoints FAIL:
00FE00 vs00FF00 and FE00FE vsFF00FF; partial blends fit predeclared tolerance,
disabled blending exact. Original oracle unchanged.6493files309dirs5clean hives,
normal shutdown delta1,33 independent files,154 archived inputs. New public build
choice/instructions/checker/tests. Three host tests/3456 pixel negatives. Initial
source generator's inherited batch suffixes corrected BEFORE build; generator
preserved as history. No actual negatives claimed on failing captures.

486 new mixed-color diagnostic e7942c5b...19661B, eight captures each default/HEL.
Explicit ZERO/ONE and ONE/ZERO exact. Four alpha stages uniquely match predefined
combined_floor256: (S*a+D*(255-a))//256 per channel. Nearest255 and separate-floor
models excluded for these inputs. This is characterization, not instruction trace,
all-alpha proof or exact ideal blending.484 remains failed.5571 synthetic and11204
actual mutations rejected;16captures262144bytes,11modules/process cold exact.
PC normal restart04:44:42UTC,6497files309dirs5clean hives,37 independent files,
148 archived inputs, no system error/warning in selected new delta. No full NTFS
allocation audit; inherited SOFTWARE typed DRM limitation retained.

487 one physical launch accepted04:50:01UTC, dashboard04:50:25UTC. No result
namespace/runner/images; NOT Windows restart or alpha result. Primaryphase6 and
late256B witness valid,1553 actual mutations reject;2SMBus operations1167polls
627910TSCticks. Witness cannot prove its own close/laterchecks/paging/Windows.
Aliasbacking790528 same as successful483: scalar alone is not failure discriminator.
Failure after last witness unknown. No speculative driver patch or repeated boots.

487 wrapper851a916d...541526B compiled from pinned482 with same483 diagnostic
implementation/new namespace. Host001 FAILED stale encoded X483/R483 checker
identities; source/log/exe preserved. Host002 only corrects checker constants,
same XBE:132 actual assembled wrapper cases (kernel/file/SMBus/TSC MODELED),
1680 transport negatives,12 modeled dispatcher cases including22/23 result bounds,
24/26 NT5 imports pass.47 package inputs archived; unchanged sample486.
Collection001 failed FTP PASV502 AFTER hook removal and all mutable cold files.
Original partial preserved; finish-collection002 only6 missing reads/absence
results, two fresh read-only sessions each, zero new writes. No launch/collection
retry. Five hives clean/raw agreement, both event logs/video/hives byte-identical,
normal shutdown delta0. Original/staged files exact. No full FATX scan;463 remains
separate. Windows Ft49/two483 shutdown popups retained historically.

All owned sessions CLOSED:484 cold56507/98495/runtime89782;486 oracle99287,
cold9438/57862/runtime64281/mutations87043;487 stage78661/observer25469/missing89295.
All short builds/reviews closed; read-only inventory found no QEMU/NBD/FUSE/xemu.
No physical/audio/PCI/USB/display driver changes, no1080i/GPU/game promotion.
Private fixtures/builds on C/WSL, C latest~24.46GBdecimal/E21.499GBdecimal; retain
20GiB projected guard, E nearly at threshold. No cleanup/backing moves this turn.
Historical untracked files untouched. Next review successful483 vs failed487
remaining post-witness/privileged entry boundary, then fresh matched Xbox
arithmetic evidence before windowed D3D presentation. No user action pending.

'''
for name in ['CONTINUATION.md','STATUS.md']:
    p=W/'outputs/engineering-notes'/name;old=p.read_bytes()
    assert not old.startswith(text.splitlines()[0].encode());p.write_bytes(text.encode()+old)
for n in ['.gitattributes','docs/graphics-samples.md','docs/graphics-roadmap.md','src/samples/graphics-ladder/README.md']:
    p=W/n;p.write_bytes(p.read_bytes().replace(b'\r\n',b'\n'))
print('Exact continuation/status recorded; historical suffix preserved.')
