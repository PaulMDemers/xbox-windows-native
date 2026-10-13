# Measurement-only351 build reviewed

Matched OFF/ON drivers compiled from exact348 tree
f9adc6373a147add130c8e619bd88ff726d80738 into tree
527cb5bff9e17ee1bfb052ac78e46a7addea5b19. Only PRIMARY_COPY differs between
build definitions. The new eligible counter/escape is described in DESIGN.

The actual counter passed980014 ASan/UBSan checks, including64-bit carry,
saturation, sticky invalid-input errors and preservation of all original348
statistics. Exact source reconstruction proves the old348 record/snapshot,
PDEV layout, planner, admission, copy and upload code unchanged. Probe changes
are only packet version/validation/tags; all drawing/audio test work remains
unchanged. Native imports, residency, local memmove instruction path and equal
warning sets reviewed. The probe is warning-free with owned NT5 imports.

New352 parser tests reject malformed counters and transport:2048 packet
checks,994 phase-placement controls. Their modeled rows are not guest evidence
and do not requalify349/350. Actual ordinary results belong to352; physical
results, if launched after that pair, belong to353. This build alone makes no
runtime, hardware, performance or release claim. Old348 escape/results remain
available and unchanged. No arbitrary system-memory bitmap fast path added.
