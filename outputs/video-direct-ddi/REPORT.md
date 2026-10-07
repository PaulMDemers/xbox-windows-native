# Direct DDI build passes host review; first selection trial fails

Both attempts are CLOSED. Never relaunch or recollect them. No physical access.
The new0107 xwndir.dll has not been qualified by this kit's guest trials.

Microsoft framebuf control001: strictPASS,54drawing cases/162pixel checks,
normal restart/dashboard,325directories6758files326directoryclusters with zero
allocation errors/orphans, five structural hives and unchanged protected/payload
hashes. No new warning/error/application events. Same96MiB1536cluster pagefile.

Candidate001: strictFAIL, expected driver identity1 but response0 and zero output.
The probe passed installation-idle and1024x576x32 mode checks, then exited before
any drawing cases or restart. After900seconds without dashboard return, a
post-timeout pause/read/resume snapshot found Explorer, no probe process and
zero bugcheck data. Owned runner then closed via capture-complete signal.
Cold integrity and strict event checks pass; normal shutdown0 and no workload
mean the trial fails. Metadata/hash checks do not qualify all arbitrary content.

Crucially, the loaded-module snapshot contains Microsoft framebuf.dll, not
xwndir.dll. Full cold registry inventory found the bound class0001\Settings
InstalledDisplayDrivers still framebuf. Preparation changed only the service's
Device0 selector and missed that nested class key. Its narrow configuration gate
therefore passed without validating the effective driver. The mandatory custom
identity prevented a false candidate PASS. Correct the fixture in NEW kit
video-direct-ddi-selection; leave all old inputs and results untouched. This
failure does not establish a defect in the authored display code or escape.

Pair-review.json's debugger:false describes the ordinary phase; pair-addendum.json
explicitly records the later candidate snapshot and incomplete selector check.
The candidate screenshot was read without pausing before timeout, with no input;
HMP screendump was unsupported, so an explicit asynchronous framebuffer read was
used. It is observation only, not candidate-identity or timing proof.

0107 sources: reconstructed tree3c664be8842518eac9dd18d92f6a3e2f78d36f73;
DLL019f5267a66cf0a018731d1a3db9f9c8ef737da5a7fbeb6965c1aa96948d0d68.
Seventeen actual-surface.c host cases pass ASan/UBSan/leak checks. Actual owned
NT5 import exports and all ten build source files are pinned. No RAM shadow,
WC, GPU acceleration, new mode or physical performance claim. GPL notices kept.

Retained host failures: build001 CRLF patch rejected before compilation; initial
shell quoting and missing clang; malformed UNC source inspection; absent optional
hivex value and registry path capitalization before disk creation. Post-timeout
decoder initially failed on a nonresident PnP string; original decoder hash/source
retained, corrected decoder labels the string unknown rather than inventing it.
No guest retry or error gate was hidden. See DESIGN.md and the failure records.
