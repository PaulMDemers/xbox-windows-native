# First-install log alignment diagnostic

Emulator-only child fixtures of the immutable pre-install fixture from
`../fatx-first-install-0101/fixture-001.json`. No physical access or new driver.
The same reviewed UI helper completes the GPU wizard, defers its restart, cancels
only the identified emulator placeholder, then gates restart on an idle queue.
This changes timing and cannot qualify unattended or physical stability.

The physical malformed warning follows the miniport Copying file line. The same
warning in the control starts at139166; padding131059 bytes aims at270225,
sector offset401 and 4KiB offset3985. The physical damaged prefix was111 bytes.
The emulator warning is220 bytes including CRLF and uses xwninf99; the physical
package used xwninf102. Neither identical text length nor identical disk layout
is claimed. Both preserved raw logs determined which warning to align.

Preparation extends only the existing SetupAPI chain with deterministic ASCII
padding, retaining the directory slot, first cluster, complete original log and
all five hives, startup, helper and driver hashes. The new allocated clusters and
only changed FAT links are recorded. Cold allocation scan is required before
launch. Source parent is immutable and each case is a fresh sibling.

Commands (WSL for offline preparation/audits; host PowerShell for runner):

1. `python3 prepare.py 001`, then `python3 audit-before.py 001`.
2. `Run.ps1 -Case 001`, then `supervise.py 001` with local emulator FTP credentials
   in XWN_EMULATOR_FTP_USER/PASSWORD. Exactly one local SITE EXEC launch.
3. Wait for owned dashboard return and cleanup; `trial.py collect 001` once.
4. `qualify.py 001`, then after Git staging `verify-evidence.py 001`.

Never repeat a recorded launch or completed collection. Case002, if used, starts
from the same immutable parent and the same padding, not case001 output.
The alignment audit independently checks the actual post-copy warning offset,
full warning bytes,111-byte prefix, unchanged original log/padding, and new
non-ASCII bytes. A clean log at a missed offset does not pass alignment.
No debugger, host recorder, logging-policy change or physical mutation.

Private disk images, raw logs and hive/media artifacts remain ignored. Compact
reports preserve actual failed or successful states without waiving a gate.
