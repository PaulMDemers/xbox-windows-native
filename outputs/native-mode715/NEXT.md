#715 CLOSED:11 native reads match kernel;680630 differs from704 target

Read REPORT,photo001,audit001,closure001. All416 photo bits decoded, signature and
zero mismatch verified;352 middle-row bits cross-checked geometrically. Native11
values equal both kernel passes. Nine preparation files audited; retained baseline
matches714. One launch, manual reset, console dashboard, no hook or host child.
Never relaunch/recollect715. Failed payload001 preserved; payload002 qualified.

Of704's11 common PRAMDAC writes, only680630 changes the observed value: actual3,
target2. This is not proof of the708/709 fault and does not qualify six CRTC writes,
later geometry/encoder or Windows1.6. Native values remain optical, not file dumps.

Next NEW716 review680630 semantics from primary sources/retained sources, then
isolate a bounded single-register3->2->3 test under the previously observed
blank/restore sequence if justified. Independently verify admission, readback,
exact restoration and visibility; distinguish write success from restored output.
Require fresh model/CPU/compiled-loader cases, frozen sources/binaries/stage readback
before hardware. If semantics or restoration cannot be justified, perform a
read-only/source investigation instead. No functional driver patch, firmware-state
borrowing, interrupt/pending-bit change or full704 retry. Preserve708/709 failures.

Original720p protected, hardware ticket retained, build/xemu released, automation
paused; networking/boot/1080i/RCT/acceleration work remains tabled.
