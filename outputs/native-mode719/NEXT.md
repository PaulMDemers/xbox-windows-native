#719 GREEN decoded: all six CR1b samples85; awaiting reset Ready

One SITE accepted2026-10-27T15:32:31.064752+00:00. User green/holding withphoto.
photo002 decodes7190000d, bridge phase4/checkpoint5/return719, payload phase5/
error719, six rawCR1b85 values, mask3f. All416bits threshold/offset checked and
352middlebits independently cross-row checked. photo001 failure preserved:
sparse glare component counted as extra cell;002 requires65percent component
fill and retains all independent sampling checks. No expected values injected.

719 writes no CR1b data. Its six observations show no change across initial,
SEQ1blank,80d3blank,CR1f57,80d3enable,SEQ1restore in this run. This narrows the
investigation toward718's explicit write but does not prove bit7 semantics or
causation across runs. No full mode/Windows1.6 qualification.

Photo preserved before reset request. Wait explicitReady, record readiness,
collect ONCE and audit source/build/report/optical pins plus allocation aliases.
719 uses payload002 (failedpayload001 retained), result212bytes, photo002 receipt
and decoder002. Never rerun/recollect a closed runtime. After closure next review
should distinguish a saved-value same-byte write from a changed-byte write,
with fresh baseline and validated bounded recovery, before further hardware.
No hook/owned host process; build/xemu released, hardware ticket retained;
original720p protected; earlier runtimes CLOSED; other work/automation tabled.
