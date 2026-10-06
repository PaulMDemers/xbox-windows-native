# Real GPU installation with unchanged physical-baseline binaries

Owned emulator experiment, 6 October 2026. No physical access or promotion.
FATX0098, video0093 and the installed Microsoft framebuf.dll are unchanged.

## First boot: installation succeeded, overall FAIL

Run001 launched once at 17:47:08 UTC. Normal PnP discovery found the authored
INF via one appended SOFTWARE DevicePath entry. The staging comparison checked
26,907 keys and 39,233 values; SYSTEM and startup were unchanged.

SetupAPI records a successful full GPU install after an initial unsigned
copy-only rejection and later acceptance by the existing client policy. The GPU
has ConfigFlags=0, class driver0001, XboxVnt5 service and exact oem2.inf contents.
Windows set service Start=3. Query removal was vetoed (type6, CfgMgr32 code23),
so a reboot was required. This does not prove live stop/removal works.
The INF copies only the miniport; framebuf.dll is referenced, not copied.
Its retained comment about packaging a display DLL is stale and is not an
instruction to stage one. The exact tested INF bytes are preserved.

The cold audit passed527 workload mappings,16 synthetic BMP API cases,
50 exact final files,34 absent intermediates and15 rounds totaling60,000ms.
Five hives traverse successfully and checked binaries remain exact. EventLog
records one normal shutdown, but the same rundll32 window-station-shutdown
popup occurred and dashboard FTP did not return within420 seconds.

An unpaused read-only HMP framebuffer attempt timed out and produced no image.
Its contribution to the stall is unknown. The host then requested owned runner
cleanup. The termination record predates the cold EventLog finding: it records
what was observable then, not a claim that the guest never logged shutdown.
There was no debugger attachment, no screen diagnosis and no inference of the
popup's device owner in this run. It remains FAIL.

## Second boot design

Run002 uses the retained installed disk as an explicitly diagnostic continuation
of failed001. It preserves SYSTEM, SOFTWARE, the video trace and first workload.
Only startup and a fresh C:\xwns99 helper folder are changed. Probe/matched sources
are identical to the original after newline decoding and replacing xwns98 with
xwns99; compiler, flags and imports are reviewed. No registry or trace reset.
The case002 manifest distinguishes inherited first-stage SOFTWARE metadata from
second-stage edits. A clean second boot cannot erase the first result or prove
an intermittent popup fixed.

## Second boot result: bounded emulator PASS

Run002 launched once at 17:58:10 UTC and returned to dashboard at18:00:36 UTC.
Cold audits pass all527 mappings,16 BMP API cases,50 exact final files,
34 absent intermediates,15 timed rounds totaling at least60,000ms, one normal
EventLog shutdown, no new popup and no unexpected event errors. First-run files
also pass their original verifier. All checked payloads/runtime binaries match;
five hives traverse. There was no debugger or framebuffer-capture intervention.

The GPU retains its installed class/service/INF registration and Start=3. New
SetupAPI lines identify an installer for the emulator PCI1B36:0005 device with
no compatible driver. They do not contain another GPU install. This supports
investigating installer ordering/timing next; it does not establish the popup's
root cause or physical device identity. One clean run is not a regression fix.

Both owned emulator processes and disk-audit processes are finished. The disks
and evidence remain retained privately. No hardware change, full allocation
scan, recovery capture or automation was started. `evidence-review.json` verifies
recorded facts; its PASS is not a product or physical qualification result.

Next: repeat bounded shutdown workloads from independent clones of the installed
state, compare installer/event timing against the unchanged failing baseline,
and handle emulator-only device support separately. Any proposed hardware
package must first pass repeated boot/shutdown and display lifetime checks.

## Independent installed-state repetitions

Cases003/004 replay the exact immutable pre-run002 fixture in separate writable
disks. They are independent repetitions of the second-boot scenario, not a chain
of consecutive reboots. Preparation verifies hashes, unchanged retained hives/
trace/first workload, exact helpers and absent xwns99 result/matched logs.
No debugger, screen capture, registry edit or driver rebuild is used.

Both repeats passed. Run003 launched at18:28:11 UTC and returned18:30:37;
run004 launched18:31:34 and returned18:34:00. Each passes527 mapping checks,
16 BMP API cases,50 exact files,34 absent intermediates,15 rounds>=60,000ms,
one normal EventLog shutdown, no new popup and no unexpected event errors.
Each preserves the first workload and exact checked binaries, parses five hives,
and retains the expected GPU registration/INF with service Start=3.

The immutable starting F: allocation and both final F: allocations are consistent:
zero orphan clusters/errors,322 directories,323 directory clusters. Files rise
from6,795 to6,847 as expected from50 payload files plus two logs. All2,127,616
preexisting reserved FAT marks retain identical positions. These deliberately
reserved emulator marks are not a report of physical bad sectors. The full scans
cover F: only. No other physical partitions or full binary archive are requalified.

Together002-004 are three clean independent replays. Each new SetupAPI delta
contains PCI1B36:0005 installation with no compatible driver and no GPU reinstall.
No new hard-error owner tracing was performed. First-install001 remains FAIL,
and no hardware candidate is promoted. All owned test/audit processes finished.

`prepare-repeats.py` creates unique seeds and refuses existing outputs.
`compare-installer-events.py` retains newdev commands and SetupAPI headings
beside event results; headings are not process creation/exit timestamps.
`audit-allocation.py` uses the established read-only NBD/range-reader crosscheck
and full F: allocation analyzer on the immutable input and completed repeats.
The allocation evidence extends003/004; it does not rewrite earlier audit scope.
See [NEXT.md](NEXT.md) for the outstanding first-install hardware gate.

## Reproduction and evidence

- `prepare.py`: create first owned fixture, refusing existing targets.
- `Build.ps1` / `review.py`: build and inspect the second-folder helpers.
- `prepare-second.py`: retain installation state and stage a fresh workload.
- `Run.ps1 -Case 001|002|003|004`: owned emulator with independent disk and leases.
- `supervise.py 001|002|003|004`: launch once through localhost4596 and observe return.
- `audit.py` / `audit-package.py`: cold read-only workload, event, hive and package
  checks after owned cleanup. The second audit also rechecks first-run files.

Use Python3 under WSL Ubuntu for disk/hive tools, with LD_LIBRARY_PATH set to
/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/x86_64-linux-gnu.
The supervisor uses XWN_EMULATOR_FTP_USER/PASSWORD and only127.0.0.1.
Do not replay a recorded launch or mutate an existing fixture to obtain PASS.

These diagnostic event checks retain previously identical SCM7000/Ftdisk49
signatures, and do not waive physical Srv2013 warnings. Original001/002 audits
have no full allocation scan; added scans cover the repeat input and003/004.
No physical qualification is supplied. Actual Paint UI behavior is separate
from synthetic BMP replay. No new recovery snapshot is eligible.
