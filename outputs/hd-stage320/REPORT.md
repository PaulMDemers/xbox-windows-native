#320 closed diagnostic

The unchanged316 loader returned error25 at failure stage4, after19 successful encoder writes. Resident loader text, request and return were pinned; all breakpoints were removed, physical-memory mode restored, and execution resumed. The guest returned to dashboard without entering the Windows workload. Cold allocation is clean:322 directories,6752 files,323 directory clusters, zero errors/orphans; five hives and58 protected files checked. Host exited orderly. This is diagnostic evidence, not ordinary boot qualification.

Interpretation correction: the original combined two-byte read at CRTC index/data ports returned index57/value0. The pinned emulator's prmcio read handler makes one VGA port read regardless of requested size. Its second byte therefore does not establish CRTC39's value. Original trace and final-review records remain unchanged.321 uses separate byte reads and captures the actual comparisons; it proves CRTC39 equals16 and the first failing timing read is PRAMDAC680804, zero versus1124. The earlier CRTC-specific attribution was incorrect.

No physical access or driver change. Never relaunch, recollect or parent this completed runtime.
