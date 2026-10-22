# 666: compare saved IF snapshots after IF-only admission rejection

Fresh source-only derivative of closed664; no interrupt-state or native network
changes. Original classification remains in BSS. The final light now reports
comparison of Frozen657 pre/post snapshot flags only when setup succeeded,
NativeSend656 was called, admission returned A656_CPU with IF as the only early
predicate, and transport was not used. Other paths give comparison unavailable.
This is a diagnostic of saved RAM. It introduces no extra CPU/MMIO/PCI reads.

captured=0 is missing, not IF-clear. captured values other than0/1 or present
post snapshot without state.mutated=1 are invalid. Both snapshot before/after
IF bits must agree. post_kind=2 means failure-path snapshot, not absent data.
IF-set capture copies flags_before to flags_after and skips indexed CRTC reads;
these are not two independent live samples. A stable snapshot does not prove
interrupts stayed constant between snapshots. No Windows/480p fix is inferred.

Final held codes (the table differs from664):
- Equal red/off: comparison unavailable or prerequisites failed.
- Equal amber/off: pre snapshot missing.
- Red/amber alternating: post snapshot missing.
- Green/amber alternating: both snapshots missing.
- Solid amber: invalid/incoherent capture markers.
- Red/green alternating: IF changed within a snapshot.
- Two green slots/two off: pre clear, post clear, admission set.
- Two red slots/two off: pre clear, post set, admission set.
- Two amber slots/two off: pre set, post clear, admission set.
- Solid green: pre set, post set, admission set.
Entry remains three red slots then green; timed green/off is not a final code.
Final-latch errors can leave earlier indications; preserve uncertainty.

Use fresh C:/xwn666, owned E:/Applications/XWNLatch666, fresh packet identity,
one SITE and180sec receiver. No hook, Windows or automatic reset. Record held
light/screen, request recovery, await Ready, collect/audit once. Preserve
ordinary720p/savedXBOX480, permanent firewall, releases and all closed failures.

Fresh666 corrects665 compile failure using compiler builtin offsets; adds a
freestanding/native-header host compile before the full build.665 remains closed.

Qualified tree 6bbdb738e430d28befa471b4c3b0b99b6adb1fff; XBE SHA256 2a168e00b8931681446ab2e88a2a80be1f8ea6587a720e59e6f9427136783d82.
Host53,760 original cases+12 boundaries,288 comparison cases+6 boundaries;
actual-header layout checked in host and i386 compilation.49 exact-linked
cases and51 artifact checks passed;20 native/display sections unchanged.
Raw I/O and NativeSend outputs modeled; no physical result yet.
