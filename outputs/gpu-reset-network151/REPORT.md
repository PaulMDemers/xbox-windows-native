# Reset network observation: one preserved FTP failure

The control passes. The candidate completes both native probes and all twelve
exact arena snapshots, but fails the original dashboard FTP return gate after the
second normal reboot. This pair is NOT qualified. See verification.json,
control001/audit.json and candidate001/audit.json; no case was retried.

The unchanged xemu build003 pair runs native150, one explicit HMP system_reset
with a live GPU marker, then native149 once on dashboard return. The private
runner adds bounded packet capture and nine sparse NVNet events. No network state,
guest RAM/registers or dashboard configuration was changed. All three phases in
both cases have matched DHCP REQUEST/ACK transaction/MAC/address evidence, guest
BMSR link-up and receive DMA activity. The failed candidate's dashboard screenshot
shows10.0.2.15, so lack of DHCP is not its demonstrated failure.

The old supervisor closes each connection after two seconds. Full handshake.json
contains forty greeting-bearing TCP flows: host FIN precedes every server greeting.
First-greeting delays are2.046431..16.271158 seconds after SYN and
2.046155..16.270989 after SYN/ACK. The narrower initial sample is not the full range.
This establishes an observation deadline problem for151; it does not establish
the cause of150 control's earlier0.0.0.0 screen. A read-only three-second banner
observation also timed out and is preserved. No emulator networking patch follows.

Both cases have complete consistent E allocation, exact new file sets, unchanged
existing E file contents/chains and no top-overlay writes anywhere in F. The
candidate's pixel/protocol/disk gates pass but its return failure remains false.
External capture-complete means cleanup, not success. Packet parsing and network
gates reject eighteen mutations, including truncation, wrong DHCP identity,
missing ACK, missing receive activity and link-down.

Raw PCAP, screenshots, disks and guest binaries stay private. Tracked decoded
reports omit FTP payload/credentials. Debugger, Windows, physical and performance
qualification are all false. See series-closure.json for eight-run closure and
hashes; physical0101/video0093,0088 rollback and immutable0.1.0 are unchanged.
