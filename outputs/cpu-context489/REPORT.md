# 489: read-only CPU-register capture passes isolated privileged execution

The new313-byte capture function reads CR0/CR2/CR3/CR4, all six segment selectors,
LDTR/TR, GDTR/IDTR, entry ESP/return EIP and TSC bounds into an owned160-byte record.
It preserves the caller's general registers and EFLAGS, including initially set
IF and DF. It performs no kernel calls, port IO, control-register writes,
descriptor-table loads, page-table access or arbitrary physical-memory reads.
The caller must supply a valid, exclusive, zero-initialized destination; this is
not a safe arbitrary-pointer API or an asynchronous publication primitive.

One fresh diskless QEMU Pentium III fixture exercised two different CR2/CR3
contexts with separate epoch records. Both exact CPU records and both36-byte
post-call register/flag frames match the independent oracle. Four memory guards
remain intact. A repeated completed record, an invalid capacity with an unmapped
pointer and ten malformed headers produce no writes. The first record remains
unchanged after the second capture and refusal checks.

The397-byte actual fixture transport passes3642 independent mutations/truncation
negatives. Review maps the313 actual function bytes through ELF load segments,
reconstructs every byte from the pinned disassembly and checks all76 instruction
rows against the read-only instruction set and local branch bounds. Fourteen
private output files rehash unchanged. Capture SHA256:
`d5bed1052a1eeab8810e15f05734b2c9795d56641bf1ddb50e1a2618a808b196`.

QEMU exited through the explicit test endpoint with code33, no exception,
deadline or fallback. All owned processes are closed. Private capsule:
C:/xwn489/host001. This tests actual privileged instructions in a SYNTHETIC CPU
context; it does not qualify physical Xbox registers, page mappings, segment
descriptor contents, atomicity, kernel memory access, Windows boot or graphics.
No XBE was built, staged or launched. Console/shared source/SDK unchanged.

The user authorized continued work until2026-10-18 14:00UTC (10a.m. New York).
The existing10-minute heartbeat was reactivated with that cutoff and current
continuation-first instructions. Final10 minutes are closeout only. User screen
availability is limited to the next few hours; ask only for a useful actual test.

Evidence: [actual run](run001.json), [independent review](final-review.json),
[build and source/tool pins](build001.json), [capture source](capture.S).
Prior488/487/486/484 results and all failures remain distinct and unchanged.
