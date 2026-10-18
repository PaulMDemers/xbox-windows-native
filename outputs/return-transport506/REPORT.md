#506 HOST-ONLY return-transport qualification

Actual Python3.14 stdlib FTP with real loopback sockets reproduced successful
login followed by passive-data ConnectionRefusedError before RETR. The server
model advertised a bound non-listening data socket; commands were USER/PASS/TYPE/
PASV. This validates the transport mechanism, not actual505 packet attribution.
505 live-readback failure remains immutable; it did authenticate the dashboard.

New probe performs connect/login/TYPE/PWD/SIZE/NOOP/QUIT only, no data channel.
It requires receipt size112 and explicitly does NOT claim receipt content proof.
Content must match independent cold audit. Shared monotonic deadline and bounded
per-operation socket timeout, replies/stages retained without credentials. Real
socket tests pass normal control flow,17failure cases,4input refusals; allthreads
and sockets closed. Actual finite waiter passes13 paths with modeled probe/clock/
sleep/sink, including45second deadline and evidence-sink failure. No liveguest or
physicalconsole access, newXBE, fixture preparation, SDK/sharedsource changes.

Host001 expected ConnectionRefusedError with1secondtimeout but Windows produced
TimeoutError; source/failure preserved.002 uses3seconds and accepts either bounded
unreachable-data outcome; actual002 was ConnectionRefusedError. No production
change between001/002. Host003 adds the finite waiter. No505 result was rewritten.
