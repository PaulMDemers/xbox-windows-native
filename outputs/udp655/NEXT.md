# Continue UDP export after host-only655

Read REPORT.md, FORMAT.md, source-audit001.json, host001.json (failed final object
check), host002.json (pass) and windows001.json (pass). All listed test instances
and654/earlier runtimes are closed. Reuse qualified source, not closed runtime
instances. No candidate XBE, console launch or listener is outstanding.

Next implement and independently test a narrow post-capture native sender using
the retained nForce path, without calling the DHCP/kernel-download entry point.
First resolve the exact call boundary, MAC source before BootResetAction's later
MAC write, descriptor mapping/alignment/cache ownership and a delay primitive
that cannot depend unboundedly on a stopped timer. Every init/TX/stop wait must
have a bound and propagated result. Test missing link, stuck timer, reset/PHY
failure, occupied descriptor, oversize packet, TX error/timeout and cleanup
failure. No NIC initialization ahead of the captured display transaction.

Do not assume existing reset is TX-only: it starts RX and acknowledges NIC/MII
status. Explicitly account for these post-capture side effects and DMA lifetime;
do not clear display pending bits or borrow firmware state. A cleanup failure
must not hand live DMA/reused memory to Windows. At most three identical packet
copies, each after confirmed prior descriptor completion; no transaction/launch
retry. Missing packet remains unknown.

Bind a fresh attempt/build token to exact source/flags and final XBE hash in an
external manifest; avoid a self-referential executable hash. Resolve private
source IP/host interface/port without publishing credentials. Verify a new
receiver on the actual wired LAN (and necessary scoped firewall admission)
before one independently admitted console launch. Never treat localhost tests
as proof of broadcast reception. Maintain reserve and leases, exact stage
readback and bounded cleanup; preserve ordinary720p/startup and savedXBOX480.

The initial physical diagnostic must be a fresh unique path and bounded launch,
with raw result/stage/error independent of capture validity. If a watched screen
observation is needed, ask only after the new candidate is tested and staged.
No broad disk logger, silent driver change or repeated654 unknown indication.
