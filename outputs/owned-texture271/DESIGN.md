#271: standalone owned four-texture control, not yet executed

The application uses the existing nxdk58427c078b4ccb0121f359b6b6c536b3b2914976 and
prebuilt libraries. It is a separate Xbox homebrew executable, not Windows code.
pbkit initialization creates application graphics/DMA objects before observation.
There is no reset, renderer switch, pb_kill, allocation release or source-texture
write between checkpoints. This does not establish Windows GPU ownership.

Four4096-byte contiguous allocations contain512-byte16x8 linear A8R8G8B8 textures
at offset256, pitch64. Every remaining byte is a deterministic guard. Patterns
are independent red columns, green rows, blue checkerboard and a low-amplitude
RGB2x2 checkerboard. The fragment program samples all four and adds them, with
RGB sums below255; alpha saturates to255. The host oracle defines the planes
independently of the guest's texel function. It checks the128-pixel rectangle and
one-pixel border,180pixels/720bytes per capture.

Vertex input0 supplies screen position and input9 supplies explicit texture xyzw
with z0/w1 to four projective stages. Generated constant c0=1 is uploaded to slot96.
The application sets linear color format, nearest texture filters, fixed pitch,
clamp addressing, all color writes and disabled blending, depth, stencil, alpha
test, culling and dithering. Shader compilation and byte-oracle equality are not
proof that these registers render expected pixels; the first runtime must verify
the predefined pixels without adapting expected output to the observed picture.

A stable extra framebuffer avoids pb_finished changing back-buffer identity.
The guest reads its explicit pb_agp_access linear alias after bounded FIFO/status
idle. Runtime must still prove this address/layout/coherence, actual surface and
source ownership. Guest allocation checks establish pairwise disjoint textures,
vertex storage and target ranges, plus texture end translations. They do not
cover pbkit push-buffer/DMA objects; independent live attestation must do that.

Sequence: initialize objects and owned allocations; textured draw; idle; capture
pixels and source guards; disable all textures; explicitly clear texture shader
stages/dependencies and issue a real flat draw elsewhere; idle; checkpoint11.
On normal return, reject initial errors, re-enable and draw unchanged textures;
idle; capture; checkpoint22; terminal checkpoint33 or error255. Checkpoint33 is
followed by a15-second capture window and HalHaltRoutine, NEVER a reboot/relaunch.
The host must capture final state and close its xemu process orderly. This is not
a Windows normal-shutdown test. No guest filesystem/network write is requested.

Each application idle poll has a10-second limit. Internal SDK initialization and
submission calls are not individually cancellable; a fresh owned runtime needs
an outer watchdog, bounded breakpoint teardown and cleanup. No host writes to
guest registers or state are needed to advance checkpoints: remove breakpoint
and resume normal instructions. The phase/cookie are written INSIDE checkpoint;
at entry, validate arguments and expected previous state, not a fabricated phase.

Compiled checkpoint address0x11000 and state0x32e10 are static build005 leads,
not live facts. Exact cdecl checkpoint body is19 bytes, state1612 bytes. Four
actual callers were decoded: early error path0x1114d, main phases11/22 at0x113fc/
0x11467 and common terminal/error call0x114f0. A first static checker incorrectly
expected only three calls; preserve its failure and corrected enumeration.
Binary review pins the XBE sections, caller bytes, source/dependency closure and
pbkit symbols needed for later live owner attestation.

No270 observer or268 release is installed. A NEW homebrew-specific attestor must
pin the actual loaded XBE/checkpoint, kernel mapping, application allocations,
current channels/objects and addresses. Before arming any observer require real
disabled bindings/cache owners, complete known edges and CPU/context ownership
acknowledgments. Existing Windows258-driver/process attestation cannot be reused
by omitting its checks. First ordinary pixel control may establish only rendering;
four unchanged generations and complete270 observation remain separate gates.

Build005 has byte-identical native sources to004 and freezes all49 actual SDK
header dependencies before compilation, verifies the same closure afterward,
and preserves49 SDK source/library/wrapper/tool pins. Shared SDK was unchanged;
this uses pinned prebuilt libraries, not a claimed full SDK source rebuild.
Four vp20compiler messages describe TEX0 mapping to attribute9, which the native
code supplies explicitly. One known nxdk-link .edata merge warning was reviewed:
the final PE has no export directory. Exact warning set is required, not suppressed.
