# Direct reserved-RAM framebuffer experiment

Candidate0095 changes the miniport framebuffer physical address from the GPU
aperture plus offset to the loader-reserved RAM offset itself. The build option
XBOX_NT5_VIDEO_DIRECT_RAM defaults OFF; this experimental build enables it.
The original bounds/geometry checks, 4MiB length, VideoPortMapMemory flags and
unmap API remain. There is no fallback that could disguise a rejected mapping.
No cache-register/page-table/GPU-mode programming or storage change is added.

Source tree: 7cd24db714d1f4fa0d44dda543e36aaed9ff58b6.
Miniport SHA256: 75ba90a6a3a77d29afd630acaca19b63f83d60801c490d78304815217ffc244c.
The full source chain, compiler hashes and flags are pinned in inputs.json.
0094 observation records are retained to verify the actual resulting physical
pages and uncached policy, not merely the address requested by the driver.

Compiled checks cover 64/128MiB reserved bases, bad geometry, rejected mappings,
unchanged mode/output sizes/unmap lifecycle, PnP and trace error handling.
They model APIs and do not prove that NT5 VideoPort accepts this RAM address.
The owned emulator then requires a normal graphics workload/restart, cold event
and payload audit, and actual first/last PTE physical-address/cache checks.
Physical testing is permitted only after that strict audit passes; one bounded
run followed by rollback to qualified0093. Backup: xboxvnt5.trace013.

The emulator's synthetic PCI resource model is a correctness fixture, not Xbox
performance evidence. Only hardware probe timing can support a speed claim,
and a single 256x128 GDI sample is not whole-window FPS or broad stability.
Keep the0.1.0 release, current0093 baseline and FATX0088 recovery paths intact.

Check reports for actual run status. No deployment or success follows merely
from compilation or this protocol description.

## Result

Candidate0095 was rejected in owned xemu: STOP0xE0580001, arguments7/0x57/
0x03C00000/0x00400000. VideoPortMapMemory returned ERROR_INVALID_PARAMETER for
the direct-RAM request. The attempt was captured and closed; never deployed to
hardware. Compiled API models had passed, illustrating their runtime limit.
