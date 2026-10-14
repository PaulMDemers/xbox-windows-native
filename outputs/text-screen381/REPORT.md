# Captured image clean; user reports clean text at720p

After the single720p launch, the user answered "Text is clean now." The current
demo remains at720p. The user then confirmed "Dragging is clean now too."
Both symptoms disappeared in this comparison. These observations,
with unchanged Windows drivers, supports a mode-dependent display-path problem;
it does not alone identify interlace timing, transfer, adapter or TV processing.
It is a visual result, not a complete new physical workload/integrity qualification.

The user saved a Print Screen image in Paint and restarted to UnleashX. Retrieved
/E/xwndemo372/text-screen.bmp twice with byte-exact agreement; private original is
E:/xwn381/capture001/text-screen.bmp. Its 1920x1080, 24-bit BMP is 6220854 bytes,
SHA256 1c849a2ef876e62b4a5fc89b266bcea246aad0c7c52a47e4f0fa951a51c971ce.

Viewed on the host, the welcome and hardware wizard text has complete, legible
strokes rather than the broken strokes in the user's TV photos. This is visual
inspection, not an independent pixel oracle. Screenshot content is a different
instant from the photos. The driver's screen-read path substitutes its RAM
shadow, so this does not verify physical scanout bytes or the encoder signal.
It narrows investigation toward shadow-to-scanout copying or the output chain;
it does not identify the adapter, TV, encoder, field timing or driver as the cause.

User separately reports adequate overall speed and distorted/jostling window
contents during full dragging that immediately become normal on release.
Outline dragging is acceptable. No moving-window capture yet; a shared cause
with the text issue is not established. Font smoothing alone is not an adequate
explanation of the photos; no font setting was changed by this operation.

At 01:23:18 UTC October14, the guarded E selector preserved the exact installed
1080i launcher in E:/xwn381/mode720p001 and installed reviewed E720p build374.
Five shared prerequisites, audio, FATX and retained demo startup were checked.
Only /E/Applications/XWNEBoot/default.xbe changed. Dashboard C was not accessed.
The single launch was accepted at01:23:26 UTC. It stays at the desktop with no
timed workload or restart. Actual runtime dimensions have not been independently
collected; the user subsequently reported clean text. Never repeat this launch.

Rollback, only at UnleashX, uses the existing selector:

    python tools/configure-e-display.py restore --policy tools/e-display-policy.json --receipt E:/xwn381/mode720p001

No new driver, emulator run, guest image or broad regression was introduced.
Prior demo378 collection and menu380 are closed; do not repeat their operations.
