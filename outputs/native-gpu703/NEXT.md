#703 CLOSED; next complete checked native480p transaction

Read REPORT.md, closure001.json and xcal-geometry702/REPORT.md. Never relaunch,
recollect or parent closed703/701/700 runtimes. Retained source/binaries and
receipts may be compared without reopening them.

Physical kernel640x480p survived native entry. Full native VPLL/selection/output
and five CRTC bytes match kernel preparation; pitch2560, format3, interlaceff.
VPLL0003c20d and selection100a0400 equal720p701. Output21101101 differs from
701's21101100. PFB bit15 remains unknown in the photo; known maskffff7fff matches
kernel. Keep all three failed optical-review receipts; no repeat photo needed
for the complete clock/stride observations.

Next build a NEW host-tested complete transaction using the source-backed
Cromwell720x480 Xcalibur recipe, not a copy of703's kernel640x480 settings.
Keep clock registers untouched under an explicit inherited-TV-path precondition;
the unchanged clocks in two observed modes narrow the design but do not prove
frequency or full initialization. Combine700 checked encoder transport/delay
with702 ownership/geometry only after providing reviewed blanking/unlock/setup,
preserved-field handling, correct owned framebuffer drawing, readback/settle,
and output-enable-on-success. Preserve interrupt pending state and PFB config.
Failure must remain held with recoverable manual reset and no automatic retry.

702 is a geometry substage, not a ready full driver. Its scope is kernel720p
allocation ->720x480 source recipe; it must not be called on703's smaller640x480
allocation. Original Conexant720p/ordinary launcher remains protected. No Windows
entry on1.6 until a complete physical pattern is qualified.

Console is at dashboard after user-confirmed reset and successful collection.
No hook, host process or VM; hardware ticket retained; build/emulator leases
released; automation paused. Networking/1080i/boot intermittency remain tabled.
