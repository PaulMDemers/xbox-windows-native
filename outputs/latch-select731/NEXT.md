# 731 prepared: GR04 selection / CR22 observation

Fresh build,27 COFF probe cases,2353 layout cases and linked-byte checks passed.
No CR22/CR33 data writes, no native handoff, timing/blanking/gate changes or Windows.
At most GR04=0/1/2/3/saved; unknown high bits refused. Actual critical CPU context
and43 raw result words recorded. Green denotes completed/restored measurement,
not proof of any CR22 interpretation. Equal values are explicitly inconclusive.

Consult stage001.json: only completed=true admits launch after exact readback.
No launch is currently requested. The watcher must confirm the1.6 is at UnleashX
with HDMI and available for TOP bar/automatic-return observation and reset if needed.
Use one SITE request with20second reply bound via physical.py; never retry an
accepted or uncertain request. Preserve launch receipt and advance continuation.

After the automatic return, record user observation, authorize collection with
collection-ready001.json, and collect once with physical.py collect. No hook is
installed. audit_collection.py verifies the seven fresh records, source/binary/
stage identities, ownership and unrelated directory entries. Preserve partial
reports/refusals/transfer failures rather than synthesizing success. If held or
black, obtain observation before a user power cycle; do not assume normal shutdown.

Interpret first/direct/reselected reads per actual GR04 readback. Compare final
saved-state checks and flags. Never treat a green picture as CR22 writable-storage
proof, infer a pending-bit mask, replaceff withfe, or promote native mode switching.
730/729 and all earlier runtimes stay CLOSED; no reexecution or recollection.
No owned VM/process remains after build/model completion. Protected720p and all
other deferred work unchanged.
