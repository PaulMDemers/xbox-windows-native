# Diffuse alpha control

Owned D3D7 RGB software device, actual enumeration/caps, 64x64 RGB32 system-memory
target. No primary surface, mode change, GPU, texture, depth or game claim.
Same triangle at(8,8),(56,8),(8,56), z0.5/rhw1; diffuse magenta over green.
Six fresh captures: clear, alpha0, alpha85, alpha170, alpha255, blending disabled
with alpha85. SRCALPHA=5 and INVSRCALPHA=6, diffuse color/alpha selected explicitly.
Each stage queries actual enable/source/destination state and records HRESULTs.

Independent oracle fixed BEFORE build/runtime: ideal partial RGB is(a,255-a,a).
Allow at most one8-bit level per channel for a85/a170 rounding. Clear/transparent
are exactgreen; opaque/disabled exactmagenta. Safe triangle interior561pixels,
exterior2199 exactbackground; boundary1336 eitherbackground or allowedforeground.
Exact edge coverage and unusedX byte are unqualified. Broad rounding, changing
expected colors after observing results, and accepting a missing stage are forbidden.

Microsoft documents separate SRCALPHA and INVSRCALPHA factors since DirectX6:
https://learn.microsoft.com/en-us/windows/win32/direct3d9/d3dblend
Pinned RosBE D3D7 headers supply actual ABI/constants. Documentation's modern
API context does not substitute for actual NT5 runtime checks.

Actual runtime modules and cleanup must be complete. Six16384-byte frames per
process; default and HEL separate processes,90second deadlines in private
controller. Normal guest restart and complete selected cold audit required.
Public batch has no watchdog and never treats process success as pixel approval.
Fresh immutable404 PCseed child and read-only independently checked1.44MB floppy;
no executed480/483 child reuse. Frozen source/tool/runtime pins, owned leases,
20GiB projected space guard; C/WSL scratch, E nearly full. On failure preserve
original outputs; no expected-image adjustment. Only PCpass supports fresh Xbox.
