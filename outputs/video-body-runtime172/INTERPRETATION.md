FROZEN170/171/172 design/parser text says the OFF comparison isolates added clock
queries. The source also branches on Enabled to update tick/read totals and do
64bit arithmetic. The actual ON-versus-OFF ratio therefore measures clock queries
PLUS enabled accounting, not queries alone. Both retain common call-count/lock
bookkeeping, so neither is an untouched112 overhead control. Preserve frozen
inputs/text and make this correction explicit in final analysis/report.

128-pair calibration measures direct EngQueryPerformanceCounter calls, not the
entire XwnProfileStart/End wrapper. Elapsed engine/copy-body totals include bounding
query/wrapper instructions and interruptions; upload-wrapper includes nested
accounting. Never subtract the calibration minimum as a known per-operation cost.
Global intervals can contain background hooks. No hardware inference or optimized
store implementation is justified by emulator-only elapsed observations alone.
