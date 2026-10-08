# RAM0109 controlled crash handoff

Fresh sacrificial emulator child from the immutable video-mode-reset prepared
fixture. Reuse the exact previously reviewed probe/trigger bytes and source;
no driver build, setting, service suppression, device-policy change or physical
access. Preserve prior failed evidence and all rollback/release artifacts.

Probe entry is the initial fixed-address breakpoint. At its actual execution,
identify the pinned kernel from two IDT gates and PE timestamp/image size; then
arm kernel-relative crash sites. Bound foreign entry hits and demand-fault
steps, retain raw CPU/owner evidence, never edit registers or guest code.
One local-emulator FTP launch, 600-second observer, at most64 stops; cleanup
removes all breakpoints and resumes. Supervisor allows30 seconds of final
output before capture/owned runner cleanup. On observer failure, wait90 seconds
instead so an entry-time host error does not terminate the guest before its
35-second trigger delay. This does not turn a failed trace into a pass.
Never stop immediately on bugcheck.

At the real E058D103 cookie, save a stopped64MiB physical snapshot and enumerate
all pages covering RAM0109 text. Compare every mapped byte against its relocated
owned PE; retain raw PDE/PTE entries for absent pages without reading through
them or forcing a page-in. Require the actual XwnUpload/DrvAssertMode entries
mapped and pinned by GDB too. This protocol does NOT qualify whole-display-code
residency: the prior strict attempt demonstrated an unmapped first text page.
Its failure remains preserved. Require the complete resident bootvid crash code,
because that is the renderer which actually executes at crash IRQL.
Repeat mapped-page evidence at dump return and require matching coverage/bytes.
Read the
bounded32-slot ownership table and actual28-byte PDEV prefix before and after.
Observe first entries of DrvAssertMode, DrvDisableSurface, DrvDisablePDEV and
XwnUpload if executed after the bugcheck. No assumption that crash takeover
deletes or disables the desktop primary. Require actual boot-video callbacks,
retained shared descriptor, independent physical-page translation and resident
boot-video text. Preserve a full64MiB physical snapshot at real dump return.

Require paired NVNet shutdown and successful genuine dump return; all65,536
captured payload bytes must match cold high-LBA pagefile bytes. Require extended
ATA writes and containment within the intended64KiB, unchanged28-bit alias,
full clean allocation, five structural hives, protected/parent payload/startup
hashes, unchanged pagefile chain/configuration and clean event history/deltas.
Normal shutdown0 is intentional; this can only qualify a debugger crash test.
No whole RAM-driver residency, recovery boot of the original image, physical qualification, arbitrary crash
timing, provider-lock interruption, new mode or exhaustive file-content claim.

Prepared parent includes unused mode124 helper and xwnram control DLL; both are
protected unchanged. Exactly the startup command and new dump helper directory
are staged. Existing synthetic null and unsupported-device policy is retained.
