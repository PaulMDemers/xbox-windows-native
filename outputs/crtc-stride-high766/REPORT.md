# Test766: kernel CR19 upper-stride control

Built, host-tested and staged; no physical result yet. Source-only lineage from
closed764 and retained765 baseline; no closed runtime reused. Next source-ordered
operation after CR17 enable: m=(720/8)*4=360, preserving CR19 low five bits and
replacing upper stride bits. Expected 10 -> 30 -> 10, then prefix restoration51.
CR13 stays80, read-only. Own recovery is newest first; CR19 undo or CR13
preservation mismatch leaves output blank and requests firmware recovery.

216 words/864 bytes. Future native result end5460 fits initialized5500, but
native page/CPU/relocation/optical validation is still required. No vertical,
encoder, PLL, scanout or CR1b/CR22/CR33 writes. No fullmode or Windows1.6 claim.

253 COFF cases,2353 layout cases,10 clock cases and source/schema/link review
passed. Exact staged XBE SHA256 e1dbf1b70e2929abab8c7f89a2eb9ad05e2eac092d0570841ccdc9129acf7ceb.
Model001 failed because its fresh-read fault remained active during final
prefix readback. Original harness/result preserved; model002 scopes that fault
to its intended phase. Guest object unchanged. Clock stack offsets reviewed
and corrected before first clock-model execution; frequency remains3375000.

Unique E/Applications/XWNMode766, no hook. Dashboard authenticated for stage.
Ordinary Windows launcher and protected720p unchanged. No VM/owned host process.
