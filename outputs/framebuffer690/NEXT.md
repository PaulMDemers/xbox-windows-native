# Next: preserve an observable checkpoint across the handoff

690 is CLOSED; incoming1.6 last verified at UnleashX with HDMI. No pending launch,
hook or host process. Do not repeat689 or690. The kernel reference matches689's
PCI and cable/settings expectations, but CPU/segment/SMBus context and the native
block read remain unobserved. Kernel framebuffer validation is complete only for
this runtime; native Xcalibur display and Windows1.6 remain unqualified.

1. Prepare a separate diagnostic loader that owns and verifies a framebuffer
   before leaving the kernel, then passes a checked descriptor to the early
   native entry. Reacquire/check the allocation on every fresh runtime; never
   use690's address as a fixed reservation. Keep inherited scanout explicitly
   labeled diagnostic, not native video initialization. Do not copy encoder/GPU
   register snapshots into a driver or borrow another firmware's setup recipe.
2. Audit the entire executed handoff, not only its final C function. The existing
   boot_xbe/xbeboot.S allocates a1MiB source and a4KiB loader, builds a low virtual
   mapping, copies the stub, disables paging and copies1MiB to02600000. Its
   allocation/NTSTATUS handling, actual stub copy extent and relocations need
   explicit review. BootStartup installs GDT/IDT and clears BSS. Existing689
   BSS spans02646e3c..0265f8e8 and stack top is02800000. Confirm anew per build.
3. Prove all source, destination, stack, descriptor and framebuffer intervals
   disjoint and reserved/owned as needed before irreversible transfer. Preserve
   the64MiB/55MiB/9MiB/316160 ordinary contract. Do not overwrite live kernel
   allocations or pretend a non-overlap calculation establishes ownership.
4. Use bounded stage writes before transfer, after assembly entry and before
   encoder access, with independently validated mapping/cache assumptions. A
   kernel picture alone does not prove post-handoff writes. Exercise actual
   compiled handoff failure/success paths and negative descriptor cases before
   staging a new image. Keep native IF/status gates; no inherited-bit clearing.
5. Only after those gates, prepare a fresh watched native hold with a clear stage
   legend. Get current watch/reset availability for that deliberate hold. One
   SITE request,20-second reply bound, exact readback, unique E/F paths. No
   Windows launch yet. Networking679,1080i and original Conexant720p stay tabled
   or unchanged respectively. The last kernel probe returned automatically.
