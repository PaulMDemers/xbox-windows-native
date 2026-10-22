# UDP diagnostic 655: transport prototype, not a console result

One immutable capture is one 772-byte UDP payload. With an ordinary 20-byte
IPv4 header and eight-byte UDP header it occupies 800 IP bytes, below a 1500-byte
Ethernet MTU. It needs no application fragmentation, disk commit record or
reassembly. A future sender may send at most three identical copies, only after
bounded completion of each preceding transmission. These are transport copies,
never retries of the display transaction or console launch. There is no ACK or
network-triggered command in the receiver.

The planned destination is limited broadcast 255.255.255.255 with Ethernet
destination ff:ff:ff:ff:ff:ff on the local wired LAN. Explicit source IP and port
configuration must come from the active private configuration. No DHCP, DNS or
ARP exchange is necessary for that destination in the retained Etherboot path.
The NIC still needs working link negotiation, DMA and transmission. No current
source, port, NIC initialization or LAN route is qualified by this prototype.

Broadcast is local and unreliable; a missing packet is inconclusive. A receiving
firewall or separate network segment can hide it. UDP can lose, duplicate or
reorder datagrams. See [RFC768](https://datatracker.ietf.org/doc/html/rfc768) and
[RFC919](https://datatracker.ietf.org/doc/html/rfc919). Tiny finite bursts avoid
turning a diagnostic into continuous broadcast traffic.

## Wire format

Integers are little-endian32; the IP/UDP headers themselves use network byte
order and are outside this encoder. IEEE reflected CRC32 covers bytes0..767.

|Offset|Bytes|Meaning|
|---|---:|---|
|0|8|ASCII XWN655U1|
|8|4|Version1|
|12|4|Exact payload length772|
|16|16|Fresh nonzero attempt token|
|32|32|Nonzero build identity token, assigned before compilation|
|64|4|Signed original apply result: -1,0,1|
|68|4|Snapshot point:1 after return,2 after original failure blanking|
|72|32|Request:8 raw words|
|104|36|State:9 raw words, beginning stage/error|
|140|252|Existing wait trace:63 raw words|
|392|188|Pre snapshot:47 raw words, including capture flags|
|580|188|Post snapshot:47 raw words, including capture flags|
|768|4|CRC32 of preceding768 bytes|

Field ordering is the same explicit ordering in
[receipt652/FORMAT.md](../receipt652/FORMAT.md). Only its data type is reused;
no disk encoder, commit sector, storage callback or flush claim is involved.
`packet.c` writes fields explicitly and never serializes native struct padding.
All stage/error/capture words are retained even when outside the654 LED
classifier. Incomplete capture is not filled from an expected timing profile.

The build token is not a self-referential executable hash. A future staging
manifest must bind the token, source tree, flags, exact compiled executable
SHA256 and attempt before launch, then verify staged bytes. The receiver requires
that independent executable pin for a physical-candidate manifest. Tokens, peer
IP and CRC detect stale/mixed/accidentally damaged records; they do not authenticate
the sender or prove hardware execution. Source phase labels remain producer claims.

## Host receiver

Use Python3, a fresh private output directory and an independently pinned JSON
manifest with `attempt` (32 hex characters), `build_id` (64 hex characters),
`expected_peer` (configured IPv4 address), `fixture` (`physical-candidate`) and
`candidate_sha256` (64 hex characters). Host tests use `host-loopback` explicitly.
Do not substitute the synthetic test tokens for a real attempt.

Invoke `receiver.py --manifest <private-manifest.json> --output <fresh-directory>
--bind <host-LAN-IPv4> --port <configured-port> --seconds 90` using absolute paths.
The receiver opens no firewall rule and sends no traffic. Start and verify the
listener before the separately admitted one-shot launch. The output directory
must not exist; closed captures are never overwritten or resumed.

It receives for at most180 seconds and128 datagrams (defaults90/64), retains
up to4096 raw bytes per datagram plus length/hash/source, and records duplicate,
rejected and conflicting records. The first valid decoded record is retained;
a different valid record for the same attempt marks the entire capture as
conflicting, not an overwritten success. Silence remains `no-valid-packet`.
Exit0 means one distinct format-valid record, not Windows success. Exit2 means
no valid record or conflicting records. Socket/file errors raise and, if the
capture has started, record receiver-error in the final summary.

The listener stays through its bound after the first packet to catch conflicts.
No process is left running by the tests. Actual host firewall acceptance, LAN
broadcast reception and physical NIC DMA have not been tested here.
