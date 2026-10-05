**Outcome: emulator PASS, physical FAIL; rolled back.** Two emulator cycles and
cold audit passed, but hardware cycle 1 produced STOP 0xB4 (video initialization
failure) before the probe ran. Original startup/driver and a fresh diagnostic seed
were restored with hash checks. No second physical launch occurred. See
physical-failure.json and physical.json. This candidate is rejected for hardware.
Removing file logging also removed diagnostic PCI reads and changed timing; this
experiment does not isolate which effect matters. Follow-up0093 branches directly
from the baseline and retains both behaviors while permitting trace reuse.

# Video repeat-boot candidate: file logging separated from PnP forwarding

Physical GDI 002 demonstrated that the 0.1.0 diagnostic miniport deliberately
stops on a reused trace file. Its trace contained41 records at the expected
marker and offset 16. The GDI harness reseed correction enabled physical 003, but
manual dashboard boots still need the file dependency removed.

## Change

Patch 0092 adds XBOX_NT5_VIDEO_TRACE_FILE, default ON for compatibility with the
existing diagnostic build. This candidate explicitly sets it OFF while retaining
XBOX_NT5_VIDEO_TRACE and the qualified PnP/geometry options. Four no-op trace
hooks replace video_trace.c. PnP START forwarding, unload wrapping, adapter setup,
geometry and failure guards remain unchanged. No framebuffer mapping, caching,
mode, FATX, HAL or loader change is part of this candidate.

The new source tree is 1c64c0146c91a7bcc7575687a56606dee48b8f58, reconstructed
from the pinned baseline plus the ordered manifest and 0092. The candidate is
0f05fabc1a576c747516728f2b89252847feca0a319042ab2a8f2ee1f09e99a4.
`build.py` uses the same reconstruction/space/tool checks as tools/rebuild-native.py
with this candidate's input lock. It requires the build lease and fresh output.
The 0.1.0 lock, tag, captured files and package remain unchanged.

Compiled x86 tests verify PnP START forwarding/status preservation, rewrapping,
and retained failure guards. The candidate imports only KeBugCheckEx and the
existing VideoPort functions; no Zw file-I/O or diagnostic PCI-read import is
present. This is compiled callback evidence, not hardware validation.

## Emulator protocol

An owned child of the qualified GDI-v3 fixture contains only the changed miniport,
a bounded two-run helper, the unchanged GDI probe, and a deliberately populated
trace copied from failed physical002. A single owned emulator is launched twice
through its dashboard. Each boot writes its own exclusive log and requests a
normal restart only after the four pixel checks and five timing loops pass.
There are no trace resets or disk-file writes by the host between the two boots.
A third helper invocation refuses to overwrite the completed logs.

`launch.json` records requests/returns; `audit.json` determines qualification from
cold payload/log/event readback. The synthetic NV2A model and emulated timings
are not physical performance evidence. No full allocation or network stress
qualification is claimed.

## Physical protocol and rollback

`physical.py` refuses deployment until the emulator audit passes and every
installed release hash matches. It preserves original startup, driver, trace,
and event logs; writes/readback-verifies xboxvnt5.trace010 as a rollback copy;
then stages only the candidate miniport and fresh xwnrpt01/xwnrpt02 helpers.
It deliberately leaves a used trace to reproduce the old boot guard. Each
collection restores ordinary startup first and verifies all expected binaries.
Cycle 2 is blocked until cycle 1 qualifies. No trace reset occurs between boots.

The physical qualifier checks each event-log boundary separately, complete
pixel/timing and normal restart logs, normal event-log shutdown, trace identity,
all expected binaries, and absence of unexpected new errors/popups. Known repeated
Ftdisk49/HID7000 records must match prior content, not just an allowlisted ID.
`physical.json` is the authoritative deployment/startup/launch state. The explicit
rollback action restores original driver/startup plus a clean diagnostic seed
without launching Windows. Do not reuse attempt IDs, delete logs, or automatically
retry an ambiguous launch.
