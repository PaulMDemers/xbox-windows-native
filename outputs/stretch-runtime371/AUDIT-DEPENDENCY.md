# Preserved incomplete audit and explicit dependency

The first control001 cold audit stopped at audit.py line72 because stretch-probe370/phase_analysis.py imports large_analysis, which was not in the original runtime search path. The guest had already completed all five samples and restarted normally. No guest relaunch occurred.

The additive audit-complete.py wrapper supplies the existing pinned hd-phase344/large_analysis.py through PYTHONPATH. It records all existing output hashes before invoking the unchanged frozen auditor, refuses a completed audit, preserves stdout/stderr, and requires every previous output and all supplied code to remain byte-identical. Control completion passed those checks; the original missing-import failure remains recorded in control001/audit-completion.json. Candidate uses the same explicit dependency, with a separate preflight record. Its runtime compiler inputs and native driver are unaffected.

This is completion of an interrupted host analysis, not requalification by a relaxed guest gate. The strict whole-boot event check, legacy graphics/audio checks, structural hives, protected hashes, allocation scan and normal-shutdown checks are unchanged. Frozen disassembly and patch whitespace remain exact through narrow attributes; no binary evidence was normalized.
