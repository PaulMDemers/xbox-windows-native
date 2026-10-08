# Matched ordinary Windows redraw correctness passes

Both155 cases pass the unchanged45-case functional protocol and strict cold
qualification. Each compares13,271,040 pixels, saves45 byte-exact reference images
and45 observed RGB readbacks, and passes independent host recomposition. Same
positions, widths, guest drivers/mode/configuration and compiled141 probe; only
the reviewed build003 xemu control/candidate binary differs. No guest source patch
or physical deployment. RAM0112 is staged into both new immutable-parent children.

Each run covers three rotated repetitions of15 equal-area/position/width layouts,
alternating memory-DIB and primary BitBlt phases. The host requires exact loop,
callback, upload and upload-byte relationships, full visibility, unchanged source
reference hashes, completion and idle pending-install checks at both ends.
BitBlt totals are65,920 control and301,056 candidate because the unchanged probe
calibrates loops independently. These counts are not an equal-loop speed ratio.
All other distinct drawing hooks remain unobserved and unqualified by155.
Both clock and quiet-counter protocols pass; comparative timing stays FALSE.

Sparse lifecycle evidence reconstructs the640x480 linear Z16 watch that is actually
alive before launch, pitch1280/BPP2, extent[0x03c64000,0x03cfa000). Both download it
during handoff. Candidate then records CPU-write eviction and invalidation; control
has no CPU-write eviction and retains it until later invalidation. Verification
ends the initial generation at its first invalidation, so later address reuse
cannot substitute evidence. Candidate also evicts the two retained color surfaces
at0x03d04000 and0x03e30000. No CPU per-store tracing, breakpoints or guest mutations.
This interval includes handoff, Windows and normal dashboard return; it is not
paired to individual GDI samples. Independent address prediction for the first
three rectangles is0/0/17,280 overlapping pixels, matching the earlier diagnostic
geometry, but those callback counts were not newly measured in155.

Both full allocation audits find327 directories,6,851 files and328 directory
clusters with zero errors/orphans. Five hives parse. Protected/installed payloads,
startup, inherited synthetic null/01B0/01B4 unsupported-device policy, display
selection and96MiB/1,536-cluster pagefile map remain correct. Both log one normal
shutdown and return to dashboard; no new warning/error/application events. No
service, event, dump setting or device-policy suppression. RGB screen readback
uses the guest display path; it is not independent physical scanout proof. Alpha
in observed32-bit pixels is outside the declared RGB scope; reference bytes are
required exact.

All owned sessions are CLOSED. Control prep91277,runner91006,supervisor28239,
cold60725,offline verifier9819. Candidate prep48975,runner82180,supervisor53853,
cold73400,offline verifier50141. Actual accepted/returned times:
control19:26:14.606795..19:31:02.127493UTC;
candidate19:34:18.329830..19:38:54.218686UTC on October8,2026.
Fresh case/disk/seed/parent/payload/source and raw-artifact hashes are retained.
Never relaunch/recollect. series-closure.json seals both cases and unchanged inputs.

Preserved host observation/error: control's final verifier was initially invoked
under WSL with a Windows closure path and failed before creating verification.json.
Completed cold stages were not repeated; the remaining verifier ran under Windows
Python. A rejected HMP screendump was nonmutating; a read-only HMP framebuffer
query/pmemsave then showed the authored probe during the control workload. The
private capture and observation record are retained, excluding comparative timing.
Candidate preparation also overlapped control runtime; future timing must isolate
both cases. No debugger breakpoints/register or guest-memory writes, and no UI
actions or popup cancellation were used.

Host tests pass754 geometry/oracle checks, eight protocol failure gates,
36 cold pixel corruptions and seven initial-generation lifetime corruptions.
The offline lifetime verifier was tightened after source snapshots to stop before
address reuse; snapshots preserve the earlier verifier and final reports pin the
actual verifier. Frozen runtime/guest inputs did not change. No speed or physical
window-drag claim. See NEXT.md for isolated timing and real-window continuation;
preserve physical0101/video0093,0088rollback,immutable0.1.0 and all failed evidence.
