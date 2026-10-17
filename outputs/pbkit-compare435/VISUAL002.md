# Watched comparison: no visual improvement

The user supplied four photographs and reported “same results.” Orange photos1/2
(before PBKit) and cyan photos3/4 (after PBKit) show the same paired outcomes:
solid black plus magenta, then solid white plus green. The two-row stripe block
remains striped in both pairs. The top-bar colors distinguish the initialization
conditions; phase assignments match the test, but the photos lack a native phase
counter. Raw photographs remain in private user attachments; hashes are recorded
in visual002.json. No new console access or test was performed for this update.

The normal PBKit initialization, including observed PCRTC_CONFIG3->2, did not
restore fine detail. Do not promote that register change as a Windows fix.
Correct CPU captures plus this repeatable parity-dependent output point toward
scanout/field handling after framebuffer generation; they do not identify which
stage. GPU fetch, encoder sync and downstream field interpretation remain open.
Two displays sharing one adapter do not independently isolate the adapter or
Xbox output. This result is not proof of defective hardware or unavoidable
interlace behavior. Field order alone has not been established as the cause.

Next prioritize evidence that distinguishes the actual field-fetch/output path.
An independently validated field-resolved capture or a controlled alternate
component/HDMI path would discriminate stages better than more broad Windows
rendering changes. Any software probe must have a defined interpretation; do not
invent a field-parity bit, IRQ row offset or reuse an SD-only encoder control.
The known-good720p baseline remains installed. No new test is queued.

Earlier frozen REPORT/RUN002/closure records correctly retain their historical
pending-answer state. This addendum resolves that question: visual outcome FAIL
for both initialization conditions, while the scoped CPU/capture checks pass.
