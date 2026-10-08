# Native CPU/GPU coherence baseline passed

The single143 run passed16 exact640x480 color and Z24S8 readbacks:19,660,800 bytes,
120,292 volatile CPU stores, two pbkit lifetimes, and an observed normal return to
the dashboard. The host oracle independently reconstructs every byte; it does not
accept a screenshot or a guest checksum as proof.

For each surface and lifetime, the GPU clears the buffer, the CPU reads it, the CPU
performs17 rounds of partial overwrites, the GPU partially clears an overlapping
rectangle, and the GPU clears the whole buffer again. Untouched CPU and GPU pixels
must remain exact. A private copy of pbkit adds only two read-only depth-address
and pitch accessors. Shared SDK inputs are unchanged.

Trace verification checks the complete transfer sequence and actual geometry.
The color surface at0x03850000 has three uploads/six downloads; depth at0x0397c000
has four uploads/six downloads before first invalidation. Both use pitch2560,
four bytes per pixel, and linear layout. The same surfaces survive pbkit
teardown/reinitialization. Later invalidation/recreation happens during dashboard
handoff; this is not evidence of an explicit device-reset contract.

Startup diagnostics record `MOUNT_E 0 1 0` and `CREATE_OUTPUT 1 0`. The separate142
failure is retained.143's FTP report transfer failed, but cold collection recovered
all files. E allocation is clean, all existing E file contents/chains are unchanged,
and the entire inherited F partition is unchanged: no top-overlay F ranges exist.

Launch15:45:51 UTC, dashboard15:46:17, cleanup15:46:18 on October8,2026. All owned
sessions are closed. No debugger mutation, UI intervention, Windows launch, hardware
access, or timing qualification. The next144 test adds a GPU clear immediately
before the first CPU store to cover an unread GPU-newer surface.
