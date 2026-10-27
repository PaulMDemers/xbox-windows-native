#719 CLOSED: six unchanged CR1b samples through setup

Photo002 decodes bridge phase4/checkpoint5/return719, payload phase5/error719,
sixCR1b85 values and mask3f. No CR1b data writes. All416bits threshold/offset and
352middlebits cross-row checks pass. Failed photo001 retained (sparse glare
component);002 excludes sparse components without injecting expected values.

Manual power-cycle Ready; nine preparation records collected ONCE and audited.
Source/build/report/photo pins and independent alias checks pass. PCI/CRTC/SEQ,
geometry and allocation words match717/718. Native values are optical; preparation
files stop at handoff_armed. No normal Windows shutdown or Windows1.6 proof.

Setup did not change CR1b in719;718's explicit85->05->85 attempt returned05 after
restore. This narrows the write investigation without proving bit7 semantics or
causation across runs. No assignment to717 unknown error or708/709 full-mode cause.
Next: review a fresh baseline/saved-value write control versus changed-byte write,
including exact raw readback and bounded recovery, before another launch. Do not
maskbit7, clear pending bits, writeCR22 or waive mismatch. Use token-aware attempt
renaming:719 is also the real720p last scanline; global719->720 would corrupt
geometry. Earlier namespace changes must not be blindly copied as a procedure.

719 and all earlier runtimes CLOSED. No launch/reset pending, no hook or owned
host process. Console dashboard; build/xemu released, hardware ticket retained;
original720p protected; other work and automation tabled. Read719/REPORT,
observation001.json, audit001.json and source-review001.json.
