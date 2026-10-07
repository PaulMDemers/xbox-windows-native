# Reviewed routine was not hit

7 October 2026 UTC. Case001 installed the GPU and shut down normally, but none
of the five breakpoints in the reviewed SetupAPI routine at778cc5a8 fired.
This is a capture miss. Static seek/write/flush code is not evidence that this
routine handles the installation logger. No logger source buffer was observed.

The runner closed xemu after the dashboard returned. The debugger disconnected
with zero records before it could remove breakpoints or resume the guest.
trace.json retains the connection/reset and cleanup errors and the breakpoint
list. Owned runner cleanup is present; no emulator process remains. Do not
interpret that list as breakpoints removed before shutdown.

Cold collection passed: normal shutdown, expected UI actions, exact GPU binding,
selected binaries/five hives, complete allocation, unchanged prefix and the
220-byte warning at270225. These are debugger-run checks, not ordinary or
physical qualification. No driver fix or cause follows from the result.

The source and sites.json are pinned by trace.json. buffer-analysis.json records
zero coverage and cold results separately. The single attempt is closed and
must not be relaunched. A legacy _lwrite call was also found statically, but its
relationship to the actual logger is unverified and no runtime claim is made.
