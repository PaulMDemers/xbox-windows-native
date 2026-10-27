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
Photo received and decoded: see photo001.json and observation001.json.
All416 bits agree across three thresholds and five sample offsets;352 middle-row
bits also agree using independently interpolated adjacent-row geometry.
Bridge phase4/checkpoint5/return7184 and payload phase5/error7184 establish that
transaction returned. CR1b saved85, target05, after-write05, restored05;
write and restoration attempt flags both1. Wait statusFFFFFFFF: not entered.
Target write readback succeeded; restore85 request read back05. Final7184
supersedes earlier restoration error7188 in this source path. The panel does
not separately establish finalSEQ1/context results or why bit7 failed to return.
No inference about717 exact error or708/709 full-mode cause.
Reset requested after photo preservation; awaiting Ready before one collection.
No repeat launch, startup hook or owned host process.

Closed after explicit manual power-cycle Ready. Collection001 read each of nine
preparation records twice; audit001 verifies exact source/build/report/photo
pins, independent allocation aliases and unchanged unrelated directory entries.
PCI/CRTC/SEQ, geometry and allocation words match716/717. Preparation audit PASS
is not native success. Native restoration FAILED; reason remains unresolved.
Dashboard reached by manual reset, not a normal Windows shutdown. No hook or
owned host process remains. Do not rerun or recollect this closed attempt.
