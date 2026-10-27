#720 photo decoded: same-value write mismatch; held orange, reset pending

Photo001 signature7200000d; bridge phase4/checkpoint5/return7208; payload
phase5/error7208. CR1b saved85, prewrite85, requested85, immediate05,
after-output-restore05; write-attempted1, samples mask7f. All416bits agree
across three thresholds/five offsets;352 middle-row bits independently agree
using adjacent-row interpolation. Original photo remains private C:/xwn720.

The single same-value85 request sufficed for this observed readback change;
it did not require first requesting05.719's no-write setup retained85.
This does not establish bit7 semantics, the cause, or full-mode708/709 failure.
No second CR1b write/retry/mask/driver patch.7208 survived final checks rather
than being superseded by7204; this is bounded code-path evidence, not broad
hardware restoration proof. Native saved-value control FAILED.

Manual power-cycle requested after photo preservation; await explicitReady at
UnleashX. Then
collect720 ONCE and audit preparation/pins separately from native failure.
No new launch or closed-runtime recollection. No startup hook or owned host
process. Console currently held; normal Windows shutdown not applicable.
