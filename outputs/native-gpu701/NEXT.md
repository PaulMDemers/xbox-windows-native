#701 CLOSED: native GPU snapshot matches pre-transfer observations

Photo decodes02a010de,02b00007,fd000000,00000003,0003c20d,100a0400,
21101100,ff835180,03c5c000,03070003. Both bars green. All320bits checked
with thresholds/offsets; middle256 cross-row verified. Six shared MMIO values
and CRTC13/19/28/39 match kernel snapshot exactly. Framebuffer matches owned
allocation/scanout. This does not qualify480p initialization or clock selection.

User power-cycled after photo capture and confirmed Ready. Eight preparation
records read twice; source/binary/private pins, staged XBE/owner and unrelated
entries verified. Runtime701 CLOSED: never relaunch/recollect. No hook, Windows
or native mode/encoder/clock programming. Kernel prepared720p. No host processes.
Console at dashboard; hardware ticket retained; automation paused.

Next: source-backed complete480p transaction design and linked failure-path tests,
using observed state only as a precondition, not copied firmware programming.
Resolve pixel-clock selection and owned framebuffer contract before encoder writes.
Read native-gpu701/NEXT.md. Original720p unchanged; networking/1080i/boot tabled.

#701 photo decoded; manual reset/dashboard confirmation pending

Both bars green. Ten optical rows:02a010de,02b00007,fd000000,00000003,
0003c20d,100a0400,21101100,ff835180,03c5c000,03070003. All320 bits
threshold/offset checked; middle256 independently cross-row checked. Native
CRTC13/19/28/39 =80/51/83/ff. Raw readings are NOT programming values.

Photo captured before requesting manual power-cycle. Await Ready/dashboard;
then record collection-ready001 and collect once. No reset confirmation or
collection yet. No repeat launch, startup hook or Windows. Host processes closed.
Read native-gpu701/NEXT.md. Original720p unchanged.

#701 launched once; native GPU observation/photo pending

One SITE accepted at 2026-10-27T03:26:07.159806+00:00 after contextual user
confirmation (Proceed). No repeat. Asked top/second bar colors and hold/dashboard
state; requested photo of all ten rows BEFORE reset. No result inferred yet.
No reset requested, no collection, no startup hook. Native data is RAM/display
only; preparation files hold separate pre-transfer observations.

All host processes/VMs closed. Hardware ticket retained; automation paused.
Original720p unchanged. Read native-gpu701/NEXT.md.

# 701 staged; awaiting current watch/reset confirmation

Read REPORT.md, review001.json and stage001.json. All host checks passed and
staging readback is exact. No launch request yet. The user was asked whether the
1.6 remains at UnleashX with HDMI and whether they can watch/reset the held probe.

1. On affirmative reply record ready001.json with continue_authorized and
   watch_reset_confirmed true. Use the frozen physical.py launch once only.
2. Ask top/second bar color and whether it holds. Request a photo of all ten
   rows in ordinary chat before reset; native results exist only in RAM/display.
3. Decode independently, preserving any failed attempt. Compare native values
   with the later collected pre-transfer snapshot without treating either as a
   programming table or proof of another resolution.
4. Request manual power-cycle, await dashboard confirmation, record
   collection-ready001.json and collect once. No startup hook exists.
5. Verify exact sources/stage/private report hashes/unrelated entries, close the
   attempt, and publish. No relaunch/recollection of a closed runtime.

The next milestone remains a complete checked native480p pattern, before
Windows1.6. Component700 is closed; clock/initial-state qualification, explicit
framebuffer ownership and bounded failure-safe output sequencing remain open.
Networking,1080i and boot intermittency remain tabled.
