# Source-backed device identification and non-stopping event recorder

The emulator's `1B36:0005` is the generic QEMU PCI test device which the pinned
xemu machine creates as a memory-controller placeholder at `00:00.3`.
See [source research and design](RESEARCH.md), `device-research.json` and its
reproducible source checks. The physical console's popup owner is still unknown.

A separate xemu executable now records selected NT5 lifecycle events without
GDB stops, guest patches or paused memory captures. This is a diagnostic tool,
not a driver or shutdown fix. The prototype is for the pinned single-CPU,
32-bit non-PAE, 64 MiB fixture only. The original emulator remains available.

## Paired validation on 6 October 2026

Both cases use byte-identical copies of the first-install idle-package seed,
the same new executable and the same 120-second guest helper. No device was
removed, installed metadata fabricated, or dialog manually dismissed.

| Case | Recording | Launch / dashboard return (UTC) | Cold result |
| --- | --- | --- | --- |
| 001 | Disabled | 19:32:08 / 19:35:07 | Bounded idle/install/shutdown checks pass |
| 002 | Enabled | 19:35:58 / 19:38:55 | Same diagnostic checks pass; instrumented result |

Both installed the GPU package, completed 120,000 ms idle, recorded one normal
EventLog shutdown, returned to the dashboard and had no new popup or unexpected
event error. Nine staged payload hashes, six reviewed runtime binary hashes and
five structural hives pass. Full F: allocation is consistent: 322 directories,
6,742 files, zero orphans and zero errors. Background Windows I/O remains;
the explicit mapping/BMP workload was not run. Other partitions and the full
binary archive were not audited here.

The enabled run captured **423 records with matching instruction bytes**,
through kernel shutdown. It did not reach the 4,096-record limit. Forty-eight
owner command lines were unreadable/absent and remain unknown; they are not
fabricated from the currently mapped process. The raw host file is retained
locally; its hash and decoded records are in the report.

The useful observed sequence is:

1. CSRSS requests termination of the GPU installer, PID 912. Its exit-handling
   entry and the installer's process-wait return follow.
2. Services attempts creation of the `1B36:0005` installer at tick 9696.
3. Another services thread enters PnP control 5 at the same tick. This is the
   [service shutdown control](https://learn.microsoft.com/en-us/windows/win32/api/winsvc/nc-winsvc-lphandler_function_ex),
   not a captured timestamp for the start of GUI shutdown.
4. Services requests termination of EPROCESS `0xff9a49a0`, PID 740, with argument
   5. CreateProcess then returns false with last-error 6; the saved token is zero
   instead of its entry value `0x8dc`. Exit handling for that process follows.
5. No captured resume site targets that EPROCESS. Kernel shutdown and the
   dashboard return follow without a hard error or popup.

The termination request precedes the failed create return; the matching exit
entry follows it. Argument 5 supplied to termination is not the creation error.
An earlier event has PID 740 but a different EPROCESS (`0xff9ca020`); it must not
be merged into this lifecycle. CloseHandle and the exact GUI-shutdown state
transition were not observed. This is a **clean comparison path**, not the
earlier failed popup path or proof of a particular token-close race in this run.

One paired run cannot establish negligible observer overhead or a fix. The
disabled control is also a newly built emulator, not a byte-identical replay of
the old executable. Its clean result is preserved alongside earlier failures.
No physical files, installed drivers, release tags, recovery bundles or automated
soaks changed. All owned processes have finished.

## Tools and reuse

- `Build.ps1` / `build.py`: owned build lease, pinned source/toolchain, generated
  fixed sites and patch, isolated executable, restoration of borrowed sources.
- `prepare.py`: immutable paired seeds; refuses overwriting an existing attempt.
- `Run.ps1 -Case ...` and `supervise.py ...`: one recorded launch per case, local
  emulator FTP only, normal return observation and owned cleanup.
- `trial.py collect ...`: resumes cold collection, adopts existing reports and
  never repeats a completed allocation scan. It requires cleanup first.
- `trial.py compare`: produces one paired result, keeping recording status and
  ordinary-run eligibility explicit.
- `decode.py` / `test-decode.py`: rejects incomplete records and never interprets
  unverified code or unreadable fields. Raw validity flags stay in every event.
- `review-evidence.py`: cross-checks executed source hashes, cold checks and the
  selected lifecycle, including PID reuse.

The first build attempt stopped at a Git ownership check before changing source.
The corrected build uses an exception scoped to that one Git invocation. Existing
nvnet modifications were preserved; build warnings and limitations are recorded
in `tool-review.json`. No global Git setting changed.

Next use this recorder for a small, predetermined set of unchanged reproduction
attempts, retaining clean outcomes too. Capture the actual hard-error path before
choosing synchronization changes. Separately scope a faithful memory-controller
model from real hardware evidence; removing or renaming the placeholder is not
a demonstrated shutdown fix. Graphics performance work need not wait on an
unbounded emulator-only popup investigation, but physical stability failures
remain explicit.
