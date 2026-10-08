# Hardware counters and coherence confirmed; emulator event gate failed

The unchanged RAM0112 driver exposes the expected identity,14hook counts, upload
rectangle count and64-bit byte total. New user probe v4 took snapshots before/
after each of five bounded loops, outside reported timings. Five invocations per
boot reuse the byte-identical166 launcher. No driver code, mode, cache, service,
dump or device policy changes. Physical temporarily used the existing158/166
display package and actual159 two typed bindings, then restored original0101/
video0093. Never deploy emulator hives. Old166 cases remain closed.

One fresh emulator child accepted23:00:15UTC Oct8, normal restart/dashboard
23:02:23, owned process cleanup23:02:25. Twenty live copy checks,25loops,
50full-screen RAM/framebuffer RGB comparisons pass. Five hives/protected hashes,
startup, full allocation322directories6721files323directoryclusters,zeroerrors/
orphans pass.23frozen input pins/source snapshots exact. No debugger/UI changes.
Host Windows offline-module import failure and subsequent absent-input refusal
preserved; WSL freeze/preflight succeeded without source repair or duplicate launch.

One physical launch accepted23:04:15UTC, dashboard observed23:07:17, collected
23:07:28/restored23:07:37. Same20copy checks/25loops/50coherence checks pass,
identity112/1024x576x32, stride4096, refresh60. Normal restart/EventLog6006, two
saved typed bindings and SYSTEM/SOFTWARE parse/header checks pass. Candidate3
payload hashes exact,44trace records/dropped0/shared acquire success. Startup
restoredFIRST; all results preserved, original display/SYSTEM restored, introduced
xwnown removed. Readback verified14baseline files and console rollback ZIP.
No full physical allocation/all-file/storage audit or release/mode promotion.

Physical measured median per operation:

| Operation | Hooks | Uploaded bytes | Rectangles | ms/op |
|---|---|---:|---:|---:|
| Black/white fill | BitBlt |131072|1|2.125|
| DIB upload | CopyBits |131072|1|2.534|
| Screen readback | CopyBits |0|0|0.960|
| Overlap right/down | CopyBits |131072|1|2.492|
| Overlap left/up | CopyBits |131072|1|2.757|

Device-global counts include incidental drawing. Nineteen of20physical writer
intervals exactly match one131072-byte rectangle per operation; fillsample4 adds
one BitBlt/one TextOut,two uploads/10184bytes. Three of five physical readback
intervals have zero uploads/bytes. Sample0adds BitBlt/TextOut,2uploads/10184bytes;
sample3adds2CopyBits/2BitBlt/3TextOut,18uploads/664176bytes. Their process origin
is not proven. Retain all samples: no noise subtraction, outlier removal or PASS
manufacture. Emulator readback all five have zero uploads. Full-screen checks
take120..195ms on hardware (median120), separately logged and excluded from loops.
These are not a new paired baseline, engine/upload latency split or window-drag FPS.

Final event review found emulator Application Popup26/type4: rundll32.exe DLL
initialization failed because the window station was shutting down. Hardware has
no popup; both application logs have no delta and both retain exact inherited
Ftdisk49. The emulator strict gate is failed for the popup as well as Ft49.
report-summary.py assertion caught this after physical collection; source retained.
The executed review/ready gate checked warning/error signatures and application
log but omitted informational system Application Popup. Physical was therefore
launched through an incomplete eligibility gate. Frozen executed source packets
are preserved; no retroactive source edit, service/event suppression or waiver.
New prospective check-eligibility.py rejects all popup types and tests actual failed
record. summary.json sets scoped_counter_diagnostic_qualifiedFALSE; functional
counter/coherence evidence remains useful, not full qualification. Investigate
actual rundll32 lifecycle in a fresh bounded child before further hardware eligibility.
Read-only startup-inventory.json examined the already preserved four SOFTWARE
hives, without guest/NBD access: Run contains mobsync.exe/logon, RunOnce/RunOnceEx
are empty before/after. This does not identify the runtime rundll32 parent/command
or exclude transient installer activity; no causal lifecycle claim.

The data narrows the rendering question: these loops generally upload only their
256x128x4 destination; no repeated full-screen upload explanation. Actual bulk
copy already uses aligned REP MOVSL (166binary inspection). Next measure engine
and upload bodies separately after checking owned NT5 timing interfaces, preserving
semantics and explicit expected fill/DIB pixels. See NEXT.md. All owned167sessions
closed:15785prep,52706/75220emulator,75280audit,32254physicaldeploy,56985watch,
30959collect. Immutable0.1.0/original0088 and failed evidence preserved.
