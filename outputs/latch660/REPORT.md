# 660: bounded UDP send with persistent result indication

Closed after one accepted launch and manual recovery. This fresh candidate uses closed659 only
as pinned source and control evidence. It freezes the original display capture,
runs the same entry latch and timed indication, and calls the unchanged native
sender only if encoding and both indication operations succeed. It then latches
a result without relying on timer delays and holds. No automatic reset or Windows.

Source tree: `ed35445d75bbf8bb255753fd67c1a0333a3c468f`.
XBE:315376 bytes, SHA256
`9e9c3f1c5ce95dc56b3cba42398cd745aaf05a3d8528d629643c4ffb3d7bedb5`.
Owned destination: `/E/Applications/XWNLatch660/default.xbe`.

## Final-light interpretation

| Persistent light | Interpretation if final latch succeeds |
| --- | --- |
| Solid green | Sender used, safe cleanup, three local completions, no returned error |
| Red/off | Native admission rejected; exact rejection code not encoded |
| Amber/off | Sender returned an error without an unsafe-cleanup indication |
| Alternating red/amber | Sender used and cleanup unsafe; DMA buffers remain live |
| Alternating green/amber | Unexpected/incomplete result |
| Alternating red/green | Entry or timed indication failed; network skipped |
| Solid red | Encoding failed; network skipped |

Solid green does not prove delivery. The independent180-second receiver must
validate source/identity/CRC and bytes. If the final latch fails, the previous
state can remain; a transient or ambiguous pattern must not be decoded as final.
No native BSS status record is exported by this LED. The raw UDP payload remains
the frozen display capture and is never replaced with transport status.

## Validation and differences

The new classifier passes1,440 host sanitizer cases. Nineteen exact-linked caller
cases execute the original LED/timer and polling latch with raw IN/OUT responses
modeled. NativeSend656 outcomes are modeled separately: this is not native NIC,
DMA, cache or physical timing proof. Cases include all five admission categories,
sender failure, unsafe cleanup, missing/incomplete use, local completion,
entry/final-latch failures, timer failures and encoder rejection. Frozen packet
bytes survive modeled producer changes. No reset path is entered.

32 source/artifact reviews pass, including20 unchanged old object sections and
unchanged display capture, encoder/bridge, original timed indication, polling
latch, native sender and admission. The pre-network indication sequence matches
659; the network call and final status classification are new. Explicit native
post-capture WBINVD remains unchanged transport behavior. No mapping/IRQ/cache-mode
changes or admission relaxations are introduced. Unsafe cleanup always holds.

Controller checks pass for one accepted/uncertain SITE and refusal of duplicate
requests. The exact controller requires a passed review and its own hash. Build,
compiled harness and prepared source pins must match before launch. The runner
owns only receiver and one launch; observation, recovery and collection are
separate, so it cannot collect concurrently with a requested manual recovery.

## Lifecycle

Configuration resolves current dashboard peer and host LAN address through the
active private session, and matches the existing permanent firewall configuration.
Fresh identity, private source/build/capture paths and a unique owned E directory
are used. No credentials, proprietary binaries, hives or raw captures are public.
The persistent Xbox-only UDP50657 rule is verified again immediately before launch
and retained afterward. No elevated helper or expiring rule is required.

All28selected files are captured twice before staging. Ordinary720p/startup and
savedXBOX480 remain protected; no startup hook. Physical lease retained, build
lease free, automation paused. Historical Ftdisk49/Popup26 remain unresolved.
The user is available to report the final light and power-cycle after the hold.
One SITE with20-second reply bound; never retry an accepted or uncertain launch.
No closed657/658/659 runtime may be rerun or recollected.

## Physical result and closure

One SITE was accepted at 2026-10-22T21:46:15.189617Z. The user reported
"Flashing red, black screen"; the bounded dashboard probe failed during the hold.
This matches the final red/off native-admission rejection category. Exact CPU,
segment, cache, PCI or DMA rejection remains unknown; no raw BSS status was read.
The unchanged NativeSend656 returns before send656 when admission rejects.
This observation does not identify a host firewall failure or qualify NIC/DMA.

The identity-matched receiver ran for 180 seconds, covering about 172.94 seconds
after launch, and received zero datagrams. Receiver exit 2 means no valid packet;
its launch_sent=false field describes the receiver's lack of launch authority,
not the independently recorded accepted SITE request. No retry was sent.

After the observed hold, the user power-cycled and replied Ready. One collection
completed at 21:48:19Z. All 28 selected files are unchanged, five hives parse,
savedXBOX480 is intact, and event histories are unchanged with no new 6006.
This was manual recovery, not a normal Windows restart or full FATX audit.
Receiver/controller/collection/audit processes exited. No startup hook exists;
the permanent scoped firewall rule was verified and retained. See observation,
recovery, collection, audit, reconciliation and closure001 receipts.
