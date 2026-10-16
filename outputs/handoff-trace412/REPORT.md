# 412: original paging handoff reached Cromwell in the emulator

One fresh owned emulator child launched the exact physical E720p launcher at
2026-10-16 01:24:37 UTC. The bounded debugger trace reached six stops by01:24:44:
original entry11100, pre-jump111f2, low relocated entry02000000, immediately after
paging disable0200000c, new CS far-jump target02000050, Cromwell entry02600000.
Original wrapper bytes and payload were pinned against installed374 XBE
6240a801...; no guest memory/register edits, only hardware breakpoints and pauses.
All breakpoints removed, physical-read mode restored, host stopped/quit exit0.
Cromwell's first instruction was NOT executed; no Windows or normal shutdown.

Actual before-transition CR0=8001003b/CR3=f000; after CR0=1003b; later CR3=0.
Both loader copies and original payload were exact, far-jump target02000050.
Low virtual backing00085000, contiguous loader physical02000000, matching
hardware allocation addresses except low backing (410 hardware00086000). This
is a distinct environment/run, not equivalence or physical failure reproduction.
Actual IDT handlers/kernel header were captured, not fully symbol-matched.
Twenty mutations of actual reports were rejected;26 private captures rehashed.

Preparation001 refused because fresh406's launcher hash differs from physical374.
No guest launched. Preparation002 changed only21 actual bytes in the same allocated
launcher file of a new private child; full mapping/local-extent comparison checked
1703936bytes, preserved allocation/entries/padding and all other disk bytes. No
shared source/SDK or physical console write. Linked existing original object code
matched every deployed byte from11100 to13000; original offsets used, not410's.
Fresh unused preparation002 parent, private runtime child/EEPROM/ports and lease.
191 frozen runtime inputs exact. Reused only an owned closed emulator executable
copy; no executed runtime disk was reused as the new seed.

Cold checks: full10GB virtual mapping, local overlays compared;55 bytes changed.
One at1540,51 in sector8,three directory-entry bytes at3628544184..4186. Strict
whole-disk equality is FALSE, and the writer is not attributed. Independent full
E inventories match all6552 file names/content hashes. The three directory bytes
are offsets56..58 (creation fields per owned layout); no retrospective gate waiver.
Full E allocation:275directories/6552files/254directory clusters,0errors/orphans;
QCOW clean, EEPROM identical. Original audit's filesystem-unchanged false result
is retained separately from the later file-content/namespace comparison.

The boot problem remains unresolved. This debug run validates only the observed
original handoff path in this emulator. It does not prove reliable ordinary boot,
physical success, early Cromwell initialization or a launch-route fix. No patch
is justified by the successful allocations/copies/transition alone.

411 separately reverified61 current physical installed/rollback/media/player
files. The user can run E:\Applications\XWNEBoot\default.xbe through UnleashX
File Explorer, then C:\xwndemo407\play.cmd in Windows. No remote launch or writes;
windowed video/audio had been user-confirmed, fullscreen frame drops retained.
The console is reserved for the user's demo while work proceeds in the emulator.
