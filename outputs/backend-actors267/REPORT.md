#267: shader work acknowledgments and context references observed

The new emulator-only observation passed its scope. Strict qualification remains
false solely for inherited Ftdisk49. No physical driver changed and no object was
released, disposed or granted to the native GPU driver.

The actual 53 retained shader-save handles and one loader now have separate,
unique lifecycle records. All 54 original work functions had returned at the
observation boundary. This is release/acquire acknowledgment of work completion,
not a claim of OS-thread exit or joining. The exact original shader source is
reconstructed by removing only the instrumentation; existing joins, work bodies
and disposal logic are unchanged.

The renderer reported its actual native render context65538 and display
context65539; UI independently reported65537. These numbers belong only to this
closed run. The query captured264 indexed uniform/transform-feedback buffer rows
and323 FBO, VAO and program attachment rows. All indexed buffer names were zero.
This covers the pinned GL4.0 interfaces and known renderer/current UI containers,
not every possible future extension or undiscovered UI object.

All four disabled texture units still have one cache edge plus one unit edge,
refcount2 each. Texture38 is actually bound to render-context unit0; textures34,
35 and36 have no observed context binding or FBO attachment. None of the four
has an observed FBO attachment. Read emu001/release-evidence.json for the complete
captured identities, ranges and proposed release requirements. No release ran.

The UI still retains numeric HUD/snapshot name26, while its actual VGA
DisplaySurface has texture0. This independently supports the prior classification
as a deleted fallback texture, not the live renderer display texture10.

The single run was accepted at22:35:01UTC and closed at22:37:27UTC on October11.
Two actual native attestations, one immutable55,678-row renderer ledger (218
pages) and1,939-row UI ledger (eight pages) completed. Both CPU-exclusive boundary
inventories acknowledged zero callbacks; context selections restored, frontend
reopened, all breakpoints removed and physical debug mode restored before resume.
Two CPU reads matched32,768 bytes with zero writes. The224 workload completed64
leases,65 allocations/releases/refusals,3,194,880 bytes,128 preflight reads and four
joined workers. Windows restarted normally and xemu exited orderly with code0.

Cold allocation has322 directories,6,728 files and323 directory clusters with
zero errors/orphans; five hives and31 protected hashes passed. All2,049 frozen
inputs and108 host dependencies remain exact. The sole warning/error is Ftdisk49;
no application event was added. No ordinary/performance or physical qualification
is claimed.

Build001 SHA75494d6eecfc579d2d7bc77fadb89584d78ed191436ee23d06237fa518b98e38
is191,717,221 bytes at E:/Codex-archive/xbox-windows-native/actors267-build001.
All borrowed source files were restored. There were79 inherited warning instances
and no new warning messages. Host ASan/UBSan tests covered4,096 concurrent records,
8,192 contenders and10,000 saturation refusals. Thirty-six synthetic negatives
and37 mutations of actual rows were rejected; pending work remains unknown.

One timing limitation is explicit: VGA metadata uses the existing main-loop/BQL
lock. The UI query's one-second budget does not independently time out lock
acquisition; the outer owned-run watchdog bounds the process. No lock stall was
observed. Future transactions must review their exact lock ordering and bounds.

All267 owned sessions are closed, including build61099 and controller52503
(runner3700/tracer100908). Never relaunch or recollect emu001. Earlier265/266 and
all failed evidence remain unchanged. Physical demo and private recovery256,
immutable0.1.0 and0088 remain preserved.
