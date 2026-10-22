# 667: read IF immediately around memory-size detection

Fresh source-only derivative of closed666 (tree
6bbdb738e430d28befa471b4c3b0b99b6adb1fff). The only BootResetAction change is
replacing its original BootDetectMemorySize call with a wrapper plus declaration.
The wrapper reads EFLAGS into RAM before and immediately after exactly one
original memory-detection call. Explicit distinct markers validate both samples.
No CLI, STI, POPF, interrupt-mask change, allocator rewrite or admission waiver
is introduced. Original initialization order remains intact.

The prior CPU and display-context classifications remain in BSS. Boundary
classification is eligible only when the saved pre/post display samples and
admission have IF set, with the prior setup/admission guards satisfied. Other
contexts report unavailable, retaining the detailed context in BSS. This does
not treat a missing RAM record as IF-clear. The unchanged sender may reject
before touching the NIC; zero datagrams alone cannot identify its cause.

Final held LED table (different from666):

- Equal red/off: boundary comparison unavailable; inspect prerequisites.
- Solid amber: missing or invalid memory-boundary markers.
- Two green slots followed by two dark slots: IF clear before and after.
- Solid green: IF clear before, set after memory detection.
- Alternating red/green: IF set before, clear after.
- Equal amber/off: IF already set before and still set after.

The last four outcomes also require pre/post-display and admission IF set.
Entry remains three red slots then green; timed green/off and dark pause are
not final results. A failed final latch may retain an earlier indication.
Solid green is a boundary transition, not UDP or Windows success.

Host tests retain53760 original classifier cases and288 display-context cases,
adding360 boundary marker/context/IF combinations and four boundary checks.
Exact-linked wrapper tests model four combinations of incoming/outgoing IF;
they check captured full flags against the live flags at each PUSHF, validity
markers, one original call, and preserved outgoing IF/stack. The memory detector
is modeled only in that host test. Linked caller tests cover55 cases with raw
SMC I/O and native-sender results modeled. No physical NIC or timing is proven.

Native review checks actual wrapper call placement and immediate post-call
PUSHF, reset call ordering, exact source bytes, and34 unchanged .text/.rodata
sections including PCI/memory detection and allocator objects. Compiler
prologue arithmetic can change non-IF flag bits; conclusions concern IF only.
Snapshots cannot prove uninterrupted IF history or an instruction-level first
writer. Existing allocator STI instructions corroborate a possible path, not
sole causation. This diagnostic does not establish a Windows/480p boot cause.

Use fresh C:/xwn667 artifacts and E:/Applications/XWNLatch667, fresh packet
identity, one bounded SITE request and180-second capture. No startup hook,
Windows launch or automatic restart. Observe the lasting LED/screen, request
manual recovery, then collect/audit once after Ready. Preserve ordinary720p,
savedXBOX480, releases/recovery, permanent firewall and all prior failures.

Actual build/review/stage/launch/outcome state is recorded in the adjacent JSON
receipts and NEXT. No physical qualification is claimed by this design note.
