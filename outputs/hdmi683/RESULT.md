# 683 physical HDMI720p baseline: passed within scope

The user connected the previously used HDMI adapter to the user-identified1.6,
enabled720p and confirmed the current dashboard endpoint. Preflight verified the
hardware ticket, existing build/source pins, dashboard access and4,836.81MB free
on E. A fresh owned E directory was staged and its contents read back exactly.

One SITE request was accepted. The user watched the test and reported, “Looks
good, yes it returned to the dashboard.” The question explicitly covered color
bars, lower stripe/checkerboard panels, white border, distortion and automatic
return. No manual launch or reset was reported for this attempt.

Three new reports were collected twice with matching bytes: before-kernel-mode,
pattern-submitted and restart-requested. They record an eligible HDTV AV pack
with720p enabled, successful kernel mode selection,1280×720×32 at60Hz, a5120-byte
stride,32-bit CRTC format,1279/719 dimension registers and1649/749 totals.
Kernel1.0.5838.1,64MiB and GPU0xd3/MCP0xd5 match the preceding682 console report.

The staged XBE and ownership record remain unchanged. Unrelated E-root and
application directory entries are unchanged; this is not a whole-volume audit.
No startup hook, Windows install, ordinary launcher change or console C-file
access occurred. The owned diagnostic and reports remain on E. All host commands
have exited, and the console returned to the dashboard with HDMI connected.

This qualifies the **kernel-assisted720p display baseline on this console and
adapter**, together with682's composite baseline. It does not qualify our native
Xcalibur initialization, Windows video driver/handoff or acceleration. The SDK's
framebuffer allocation is not the native Windows reservation contract. Keep its
register values as observations, not a configuration to transplant.

Next is a separate native480p Xcalibur integration following
[681's remaining gates](../xcal681/NEXT.md), with a pattern-only hardware trial
before Windows. Networking and1080i remain tabled. This runtime is closed;
subsequent tests need a fresh identity and output namespace.
