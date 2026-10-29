# Test807 QUALIFIED: kernel CR07 line-compare high bit

Actual compiled COFF974 fault cases, layout2353 cases, clock10 cases and
frontend26 cases PASS. Linked executable bytes and source-only delta verified;
sources001 freezes all active helpers. XBE SHA256
d89f81ff2518df3214d20841ab7f478884f4d634b39e7cfeccc06c878e2d6927.

Pinned704 lines104..107 set line compare m=3ff. CR07 after the805 prefix is
3E; target3E. This is deliberately same-value: dropped write or dropped undo
cannot be distinguished at this baseline. Forty added faults cover admission,
readback, wrong writes, coupling and recovery; bad recovery inhibits output.
Thirty-one recovery masks, eight neighbors including CR15=DF. Own saved CR07
is recovered before CR15 and earlier blank-start stages. No native handoff,
encoder/clock change, full-mode replay or Windows desktop support claim.

Preserve qualification-failure001: layout invocation without lease was rejected
before execution. Correct invocation under the exclusive lease passed. Clock
stack offsets independently updated from this build's actual disassembly.

Dashboard001 authenticated. No stage or SITE yet, startup hook, owned process
or running VM. Next exact stage/readback, one20-second SITE, then authenticate
dashboard and collect seven reports once. Automatic return expected after15s;
if still offline after two minutes ask for screen/reset. Do not retry a launch.
Native808 only after justified807 coverage. Never reopen CLOSED runtimes.
