#714 CLOSED: GREEN CR19 changed-readback/restoration checkpoint

Read REPORT, observation001, collection001, audit001, closure001 and model-scope001.
One accepted launch, GREEN holding, manual reset, nine files collected and audited.
Preparation PCI/CRTC/SEQ/geometry/allocation match713. No hook or host process;
console at UnleashX. Never reopen, recollect or relaunch714.

Next NEW715: read-only capture of704 common-setup PRAMDAC register set before
selecting further write/restore boundaries. Existing snapshots omit several of
680884/888/88c/890/894/898/89c and680630. Capture all11 setup values in a bounded
result with independently checked offsets/widths and visible/decodable output;
compare actual kernel versus native reads separately. Do not import unobserved
firmware values into programming. Prefer kernel-file capture plus native optical
confirmation; native RAM is not persisted by old preparation files. Do not change
encoder, timings, PLL, interrupts, CR11, routing/shadow masks or framebuffer format.
Review register read semantics and validate fresh source/binary/linked models
before hardware. No blind704 full-transaction retry. Preserve708/709 failures.

714 supports specific CR19 changed10/full-byte readback and exact51 restoration,
not all extended write access, key causality or whole704 setup. Temporary pitch
change is explicit; see model-scope001 correcting inherited broad report label.
No native mode/Windows1.6 qualification. Original720p protected; automation paused;
build/xemu released, hardware ticket retained; other work remains tabled.
