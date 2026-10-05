# Reconstructed miniport control

One emulator boot using the baseline miniport from the pinned reconstruction overlay, without0093. Same base disk, settled runner, graphics probe and clean trace as the captured-driver control. Only the miniport bytes differ; no HAL/loader/FATX replacement. Source/build evidence is in the reconstruction package and rebuilt-overlay-validation. No physical access.

Result: strict PASS, one normal restart and no popup. All four pixel checks, five timing loops, baseline payload checks and EventLog6006 passed. Code/data/import/resource/relocation sections match the captured baseline.
