Source review836: exact installed FATX build8e12297c/binaryba62acbb confirmed.
Root-size and FirstCluster1 fixed-root assumptions are real source limitations,
but FATX enumeration bounds its cache maps. They do not by themselves establish
the STOP0A cause. Historical same-PC rename failure used invalid cache offset;
836 has no stack/offset capture. No driver patched/built/deployed. Next collect
836 after authenticated dashboard return, preserve file/log changes, then obtain
an offending operation/offset or controlled reproducer. See storage-review001.json.

# Boot836 reached Windows kernel; STOP0A at ntoskrnl+46167

User photo screen001.json: IRQL_NOT_LESS_OR_EQUAL, arguments18,2,0,8244F167,
kernel base82409000 timestamp4b7a1bd5. Readable Windows blue screen, not desktop.
FATX root fix passed the previous SYSTEM.ALT boundary. Do not infer root cause
from the fault address alone. See fault-analysis001.json for pinned symbol mapping.

836 remains OPEN pending return/collection. User asked to power off/on and leave
UnleashX. Independently authenticate dashboard, no hook to remove, collect836 once,
audit installed files and boot traces. No relaunch. No owned host runtime.
Next diagnose Windows kernel failure with fixed720p retained; no mode probes.
835 CLOSED. Old automation paused, direct Windows desktop work authorized.
