> Subsequent physical result: see [PHYSICAL.md](PHYSICAL.md). The original host-only report below is retained as its historical scope.

# CPU context adapter490 — compiled, host-qualified; no console launch

The new wrapper adds two read-only CPU captures to exact487: before the original
handoff witness IO and after its successful close. The new context.bin packet is
400 bytes. This is diagnostic instrumentation, with extra code and IO, not a
boot fix. No console file, ordinary launcher/startup, driver, SDK or720p setting
was changed. The intermittent physical failure remains unresolved.

Diskless privileged host001 passed46 cases: two complete CPU-context pairs and44
refusals. The actual adapter, byte-identical313-byte489 capture, original witness
instructions and original comparison/reset/flush helpers executed. Two synthetic
CR2/CR3 contexts were observed; all original handoff registers and flags were
restored, including IF/DF variation. File API outcomes, allocations and refusal
endpoint were explicitly modeled. This fixture does not test actual Xbox kernel
IO or the original refusal cleanup. One owned VM exited33 without exceptions,
deadline or fallback and is closed. Its1887-byte transport is retained privately.

The separate full001 harness executes the actual assembled wrapper and original
refusal cleanup through150 cases, including18 new context IO failure paths.
That harness substitutes a debugger trap at capture entry and models CPU/kernel/
file/SMBus/TSC facts; it traps the loader CLI before execution. It does not repeat
the privileged capture claim. Actual privileged execution is supported only by
the separate46-case fixture. The XBE file was not modified by this runtime test.
The new pre/post admission failures20/21 run in the privileged fixture; add those
specific cases to the full cleanup harness before physical packaging.

Independent validation rejected4067 actual fixture transport mutations and
truncations. A separate decoder accepted28 complete modeled-CPU context packets
and129 refusal records from full001, rejecting5241 additional mutations/partial
outputs. A complete context packet can coexist with failure of its own later
write/flush/close; decoding it never proves handoff. The new refusal extension
retains old1..19 conditions and explicitly describes20..25. Return addresses and
stack identities are checked against separately pinned symbols/original frames.

Private compiled XBE: C:/xwn490/build001/default.xbe. Exact digest and size are in
build001.json and validation001.json. Full1024-byte privileged loader, original
payload/font, original entry/imports and313-byte CPU capture are byte-identical
to their pinned parents. Undoing the two witness calls and namespace change
reconstructs original487 witness source exactly. The fixture-only linker warning
about a writable/executable LOAD segment is reviewed as its deliberate flat test
layout; the Xbox section permissions were not changed. XBE build log is empty.

There are no new failed build/run attempts in490. Closeout001 failed before any
receipt/note write because it expected passed/status in the generation receipt,
which instead uses generated:true. Its source/failure are preserved;002 accepts
that explicit provenance field. Existing488/489/487 failures
remain unchanged. Host artifacts are small and onC; noE allocation, backing move
or historical deletion. No page walk, descriptor contents, atomic snapshot,
cache/interrupt/physical boot qualification, Windows result or D3D promotion is
claimed. Context register equality does not exclude an ABA change between reads.

Read NEXT.md for remaining controller/physical packaging work. Never rerun
host001, full001, build001 or the consumed validation/transport IDs.
