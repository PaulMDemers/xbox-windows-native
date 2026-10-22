#654 watched single-comparison test

Read REPORT.md, source-review001.json, build001.json, compiled-wrapper001.json,
review001.json and the actual preparation/stage records.100 linked-wrapper cases
and9,600 host cases pass. Only the651 LED header changed; the complete captured
register data is still RAM-only.653 native storage integration is deferred.

If preparation/staging is incomplete, preserve its exact failure and diagnose it
without overwriting records or issuing a SITE request. No startup hook exists.
If staging is complete, wait for the user's readiness to watch the front LED and
screen. Ask for the ONE20-second pattern after the dark delimiter, not four slots.
Green/off=matched subset, red/off=CRTC only, amber/off=FP/general only,
red/amber=both, red/green=unknown. Green/off is not boot success.

After explicit watched readiness, record ready001.json with the user's actual
response, then use physical.py launch exactly once and start observe.py once.
Accepted or uncertain SITE must never be retried. The observer deadline is600s
from launch and it owns collection if collection_requested is true. No rerun or
recollection of a closed runtime. If it expires, preserve the result and establish
actual screen/ownership before any separately admitted collection.

On Windows desktop, request Start/Shut Down/Restart before collecting. On return,
audit exact retained files/hives/new events, preserving Ftdisk49/Popup26 limits.
No selected-file audit claims full allocation health. Close the attempt with raw
LED/screen observation, capture interpretation only where supported, launch and
process state, and no-data limitations. Do not infer a functional clock/table fix
from a match, or which register differs from a mismatch. Keep protected720p,
ordinary startup, releases and private recovery unchanged.

Do not silently extend this into a retry series or another disk logger. Choose
the next narrow source comparison from the actual observed result.
