# Candidate0093: clean initial trace control

Exact same driver, settled runner, probe and base fixture as video-trace-reuse-settled. Sole initial payload difference: a clean 4096-byte trace seed instead of a hardware-generated populated trace. Two ordinary emulator boots; the second reuses the first boot output without host reset. Original failed audits are retained. No physical access.

Outcome: strict PASS. Both boots, both normal shutdowns, all four pixel checks and five timing loops per boot passed, with expected payloads/valid trace and no new popup or unexpected error. No host trace reset occurred between boots. This single clean-start series does not prove that initial trace content caused the earlier intermittent popup. Physical testing follows this exact initial-seed protocol using video-trace-reuse-settled/physical.py and its same compiled runner.
