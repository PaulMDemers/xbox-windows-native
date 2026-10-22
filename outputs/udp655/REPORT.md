#655 host UDP packet and receiver pass; native sender not installed

The user's UDP suggestion is practical enough to pursue. Retained Xromwell
already includes Etherboot's nForce/forcedeth NIC driver and UDP/IP implementation;
the actual654 link map contains nic.o, xbox.o and forcedeth.o. This is source/link
evidence, not evidence that the NIC is initialized at the failing display stage.
`source-audit001.json` pins the source tree/files and retained link-map evidence.

The planned boundary is: preserve the original apply result, stage, error, wait
trace and pre/post RAM snapshots first; then enter a separate bounded network
export phase. This phase must not move NIC setup or DMA ahead of the display
measurement. On failure, export would precede the existing reset. On success,
continuation requires confirmed NIC shutdown and safe memory ownership. Added
code/layout and post-result timing remain experimental changes, not an identical
baseline boot. No such native hook is installed by655.

## Why the existing networking cannot just be called

In retained651 source, BootResetAction performs PCI setup before display, but
the later MAC programming and normal Etherboot entry are after the relevant
display point. The normal etherboot() entry also starts configuration/download;
it is unsuitable as a diagnostic-only call. The direct broadcast branch in
nic.c avoids ARP, but ip_transmit returns1 after dispatching a void NIC callback.
That result does not establish transmission or reception.

forcedeth_probe ignores forcedeth_reset's return. forcedeth_transmit copies the
supplied length without a local buffer bound, reuses one of two descriptors
without checking ownership and does not await completion. Initialization has
four RX descriptors too: set_multicast calls stop_rx/start_rx, so this is not
a TX-only initialization even though another start_rx call is commented out.
Static arrays and virt_to_bus (virt_offset initially zero) need actual mapping,
alignment and cache/DMA validation at the chosen hook; link-time addresses alone
do not establish safe bus access.

reg_delay has a finite iteration budget but calls udelay -> wait_us, whose
hardware-timer dependency can still hang. Several setup/stop return values are
ignored. Reset/PHY setup acknowledges NIC/MII status and changes device state.
Those are deliberate transport side effects needing a reviewed post-capture
policy, not a passive register read or permission to clear display pending bits.
No firmware state is borrowed, no initialization moved earlier and no validation
condition waived. The existing NIC path is unchanged.

## Removing the654 ambiguity

654 admitted only result1/stage5/error0 or result-1/stage255/error22, with a
complete post capture and a match mask0..3. Red/green plus dashboard therefore
did not identify the failing wait. The new packet preserves the raw values:

|Original outcome|What remains visible|
|---|---|
|Prewrite rejection/result0|Raw stage/error, request and capture flags|
|SMB failure|Original errors11/12/13, without collapsing into unknown|
|Sync wait failure|Error21 and stage|
|Vblank wait failure|Error22 and existing failed-wait/aggregate trace|
|FP dimension readback failure|Error23|
|CRTC readback failure|Error24|
|Success|Result1/stage5/error0 plus capture validity independently|
|Incomplete pre/post capture|Raw capture flags and values, never inferred defaults|

These are source-enumerated possibilities, **not findings about physical654**.
Capturing a packet would still not imply a Windows boot or normal shutdown.

## Validation and failures

host001: the C encoder passed845 ASan/UBSan checks and the independent Python
decoder/localhost receiver passed7035 checks across64 synthetic records and
six socket captures. The final freestanding object check failed because the
compiler default produced an unresolved _GLOBAL_OFFSET_TABLE_. That failure,
original build script and private logs/object are retained; host001 is closed.

host002: a fresh build with explicit -fno-pic/-fno-pie passed the same checks,
and the i386 freestanding encoder has no undefined symbols. These checks cover
exact independently constructed bytes, all6176 single-bit corruptions of one
packet, truncation, invalid identity/result/phase, output bounds/canaries,
duplicates, conflict, silence, unexpected peer, oversized packets, packet/time
bounds and refusal to overwrite a closed capture.

windows001: the same pinned encoder output and receiver source passed7035 checks
and six fresh localhost captures under Windows Python. Actual LAN broadcast,
firewall admission, Xbox timing/link/DMA, cleanup and delivery remain untested.
Only loopback packets were sent. One source search used a nonexistent boot_rom
path; corrected via rg --files, with the failure recorded in source-audit001.

All test processes exited. No Xbox file, startup hook, firmware, ordinary720p
launcher or savedXBOX480 changed. No XBE was built/staged/launched and no closed
runtime reopened. Physical lease retained, automation paused; dashboard remains
the user's last observed console state, not a fresh connectivity observation.
No acceleration or new console-revision support is claimed.
