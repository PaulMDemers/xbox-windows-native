#718: optical status for the unchanged CR1b transaction

717 returned ORANGE; no numeric result established whether the bridge refused or
the CR1b transaction failed.718 retains that transaction and kernel setup apart
from attempt namespace and adds13 rows of32 bits on a gray panel. Row0 is7180000d.
Rows1-3: bridge phase, checkpoint/refusal and return; rows4-5 payload phase/error;
rows6-9 saved/target/readback/restored CR1b; rows10-11 attempt flags; row12 wait
status. White1, black0, MSB left. See optical-schema001.

Renderer runs only on existing admitted-framebuffer return/refusal paths after
status-bar drawing. It is never called from bridge_fault and performs no device
I/O or GPU-register writes. Fixed owned metadata offsets and stack only; panel
and all cells remain in1280x720x32 framebuffer. Early faults may still lack data.
Bridge phase2 means payload was not called; phase4 means it returned. Bridge
checkpoint5 remains on a returned call and is not itself a failure code. Payload
zero fields before a call must not be mistaken for completed operations.

Native target remains CR1b85->05->85 with exact readback and bounded restoration;
no masking, new functional writes or target change. A successful future run does
not resolve closed717 retroactively or qualify sustained05/common setup/Windows.
Preparation files are not native result dumps; a photo is required before reset.

Host checks passed:131379 ownership, four ASan/UBSan pages,12 fresh CPU cases
(all closed),76 isolated whole-framebuffer optical cases and186 transaction
models with full rendered-image comparison,23 nxdk page and372 ownership cases.
Linked report table checked against schema; bridge code ends at0x558 (<0x800);
payload5120 padded9916,17relocations/four absolute.

One SITE accepted2026-10-27T07:19:02.166180+00:00 after exact stage readback.
Asked SECOND bar and holding state; requested photo of all13rows and bars.
Observation/photo pending. No reset requested. No repeat launch.
