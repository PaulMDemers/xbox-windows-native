# Windows480p635 closed: descriptor, drawing and normal restart pass

The unchanged native633 candidate booted a fresh child of never-executed466.
Windows reported720x480x32 at60Hz. DirectDraw GetSurfaceDesc returned flags0x100f,
720x480x32 and2880-byte pitch. All three GDI upload/overlap/readback cases had
zero mismatches. Probe completed with zero failures and a normal restart request.
Cold readback found one new EventLog6006, unchanged protected files, five parsed
hives,277 directories/6556 files and no allocation errors or orphans. Owned
host/controller exited0 without forced kill.635 is CLOSED; no rerun/recollection
or runtime parenting. See audit001.json and final-review001.json.

The optional miniport handle could not be opened (reported error5), so the
current-mode IOCTL was NOT observed. No access policy or driver was changed.
The primary descriptor result does not restore634's unsupported primary Lock.
Ftdisk49 and Removable Storage Service116 keep strict qualification false.
The probe logs GetLastError after logging the failed open; error5 is the recorded
value, not independently preserved immediate last-error state. Handle failure
itself is explicit. This limitation does not alter the descriptor/GDI result.

A read-only framebuffer view confirmed the owned login screen; one submission
of retained private installation credentials reached the probe. No blank-login
attempt was made in635. No unattended-logon or physical480p result is claimed.
Host parser checks passed153 negative cases plus4 branch positives/23 negatives.
Captures/hives/credentials and executable assets remain private.

A separate read-only physical inventory found the development dashboard and
protected720p intact. Installed FreeLoader/config/HAL/miniport/ownership DLL
hashes differ from the466 fixture. Historical415 classifies the latter two as
PE metadata-only, but loader/HAL differences are not fully classified. No console
file was written and no SITE request was sent. Preserve two inventory helper
import failures before connection. Match retained installed assets in a fresh
fixture before relying on this Windows result for the physical trial.
