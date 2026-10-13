# Create-only installation continuation

The original `stage.py` has a forty-minute bound. Its live process and journal
must be allowed to close before any continuation runs. Never launch a second
copy of that script or overwrite its final receipt.

`resume001.py` is a separate, one-shot continuation permitted only for the exact
closed `Total stage deadline` failure. It verifies the original journal hash,
package hash, contiguous file prefix and completed directory creation. It then
inventories all four owned roots, refuses unknown or missing completed files,
and rereads every existing file before writing anything. A journaled but
unacknowledged file may be retained only if its complete bytes match. Partial
or changed files refuse; this script does not repair or overwrite them.

Only absent package files are created, with the launcher last. All created
files receive complete readback. The original F installation's protected files
and five hives are checked before and after. Xbox C is never accessed. Normal
startup remains installed; neither staging script has a boot or deletion API.

The continuation has a separate two-hour bound and journal. The original failed
receipt remains immutable; downstream scan/boot controllers would need a new
reviewed version that explicitly consumes the successful continuation receipt.
The twelve host cases test the actual transaction with modeled FTP operations,
including corrupt readback, foreign paths, missing files, races and uncertain
prior completion. This is not a physical continuation result.

A read-only inline journal check initially omitted the derived loader directory
from its local expected set and refused. The actual continuation already derives
all parents exactly as the original stage does; no runtime input or gate changed.
