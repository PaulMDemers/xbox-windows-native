# Incomplete independent color-cursor capture; strict FAIL

Candidate001 captured 75 cursor phases and 24 restored-background frames, all
exact: 9,732,096 RGB comparisons and zero mismatches in the captured data.
The observer then rejected its cursor-marker ordering assertion. It had not
recorded the failing marker's raw arguments, so the exact unexpected event is
unknown. This is an incomplete observer result, not a demonstrated guest marker
skip, cursor defect or corrected observer bug.

The observer removed all breakpoints and resumed the guest. The guest completed
all 26 cases, with exact readbacks, 78 state phases, normal shutdown count 1,
dashboard return, clean strict event gates, full consistent allocation, five
structural hives, protected/payload/startup hashes and unchanged configuration
and pagefile. These cold results do not replace the five missing framebuffer
captures or qualify this as an ordinary run.

verification.json explicitly reports passed=false, strict_diagnostic_passed=false
and ordinary_qualified=false. The separate verify-partial.py checks all retained
raw files, references, resident pins, closure and cold results, requires this
exact incomplete case and cannot turn it into a pass. The original frozen full
verifier assumes complete pairing and is preserved unchanged.

350 resident pins include all 11,668 relocated display.text bytes. No guest
memory/register forcing, UI intervention or physical access. Same probe123 and
unchanged RAM0109 driver as the ordinary color-cursor PASS.

All owned processes CLOSED. Never relaunch or recollect this attempt. The fresh
video-color-scanout2 child records every stop and single-step transition plus raw
marker arguments before assertions, with unchanged strict ordering and pixel
requirements. Any success there must remain distinct from this retained failure.
