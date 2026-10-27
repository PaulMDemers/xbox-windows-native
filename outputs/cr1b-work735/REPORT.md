# 735 CLOSED: CPU-only work between direct CR1b reads

Fresh source-only derivative of734; same single05 write, prefix data writes,
cleanup, full-byte deferred predicate and device-read address sequence. After
first direct read,4093 fixed rotate/xor/decrement iterations execute using CPU
registers only. Iteration count, terminal counter and checksum are appended to
115-word record. No extra device access or wait-for-interrupt. This is bounded
intervening work, not calibrated time. All earlier runtimes remain CLOSED.

60 actualCOFF cases,2353layout cases,14 schema negative cases, source delta and
linked main/probe/layout instruction checks passed. Dynamic models include
hypothetical changes after first read versus after eight reads; no model proves
physical semantics. Exact data-write/recovery sequence and full-byte rejection
remain. No CR22/CR33 write, mask, status clearing, native fullmode or Windows.

Primary-source lead: NVIDIA-authored nv3ref.h (1996-1998), distributed in svgalib
1:1.4.1-2, names register1b bit7 UNDERFLOW_WARN and low three bits BURST_LENGTH.
https://sources.debian.org/src/svgalib/1%3A1.4.1-2/src/nv3ref.h/
This is NV3 evidence, not an NV2A specification. It motivates an underflow/status
hypothesis without admitting a mask or reset. Exact retrieved page is private;
reference001.json preserves its identity. Unrelated-chip results excluded.

User explicitly authorized continued self-reporting automatic-return hardware
runs without a watcher; stop and ask if console hangs. File report and dashboard
return are evidence; expected screen color is not a human observation. No hook.
Unique E/Applications/XWNMode735, exact readback verified. One launch accepted20:42:43UTC; collected once and audited. One
SITE request20second bound, neverretry accepted/uncertain. Bounded180second
read-only reachability; collect once after return, audit new files. If offline,
record state and stop launches. Original720p/ordinary launchers unchanged.

## Result

First direct read05, remaining15 direct85; all16 reselected85. CPU loop completed
4093iterations, counter0, checksum793A7EFE (decimal2033876734). Two630reads2.
Deferred check15 rejects05vs85; cleanup mask0 and selectors/flags restored.
Actual context, saved/checked/restored fields2..79 match734. No8-read requirement
for this observed transition. It does not exclude the first read initiating a
later change. Automatic dashboard return inferred from durable restart request
and FTP reachability; screen color unobserved. First reachability probe timed
out, second succeeded; failure is retained. Seven files collected once/auditPASS.
No hook/process/VM. All735/prior runtimes CLOSED.
