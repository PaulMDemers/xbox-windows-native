# Physical setup follow-up: read-only snapshot

At23:00UTC on6October2026, dashboard FTP was reachable and the installed
FATX0098/video0093, boot chain, rollback and normal startup matched the expected
hashes. `preflight.json` records the checks. `capture.json` records a read-only
copy of SYSTEM/SOFTWARE, SetupAPI and both event logs. No remote file was written
and no Windows launch was requested. Raw snapshots are private artifacts.

`decoded-state.json` enumerates the preserved PCI registry entries and their
driver bindings. These include historical PC and emulator devices; the registry
is not a live bus inventory. The latest physical SetupAPI client-install command
names10DE:01B0, with no compatible driver. The GPU has its boot-time service but
still lacks a completed PnP Driver binding and has ConfigFlags0x400. DevicePath
is the normal Windows INF directory. The successful xemu null package matches
1B36:0005 only and is not a hardware fix for this state.

The decoded event files are a current baseline, not a new boot result. Historical
popup/application records and Srv warnings remain intact. Undefined CP1252 bytes
in SetupAPI are rendered as explicit backslash escapes; raw bytes and SHA256 are
preserved. Structural registry decoding makes no claim about active windows.

Hardware follow-up must keep the supported GPU package distinct from unsupported
APU/SMBus/other functions. Do not mark an actual device supported by assigning
xemu's synthetic policy to it. A bounded observational boot can identify current
wizard state, but must not force restart while installation remains pending.
The existing physical strict soak failure remains; no new recovery capture is
allowed from this snapshot alone.
