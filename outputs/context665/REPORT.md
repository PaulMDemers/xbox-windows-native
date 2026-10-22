# 665: compare saved IF snapshots after IF-only admission rejection

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

Use fresh C:/xwn665, owned E:/Applications/XWNLatch665, fresh packet identity,
one SITE and180sec receiver. No hook, Windows or automatic reset. Record held
light/screen, request recovery, await Ready, collect/audit once. Preserve
ordinary720p/savedXBOX480, permanent firewall, releases and all closed failures.

CLOSED without physical access: host tests passed but native compile failed
because stddef.h is unavailable under -nostdinc. Preserve build001 and logs.
Fresh666 will use __builtin_offsetof and add a native-header preflight compile.
