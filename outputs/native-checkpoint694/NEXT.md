# Next after694: bounded native reads with a visible result

694 is CLOSED. User-observed GREEN held header supports the checked native
framebuffer write after paging removal. User manually power-cycled; eight exact
reports collected and local hashes verified. Incoming1.6 is at HDMI UnleashX.
Read analysis001.json and REPORT.md. Do not rerun/recollect694 or any closed VM.

The known-good diagnostic transition is narrower than689's full native entry.
It does not establish689's failing phase, encoder initialization or Windows1.6.
The next fresh diagnostic should distinguish transition success from read failure:

1. Preserve694's verified allocation custody, owned descriptors/stack, explicit
   cache/interrupt/paging changes and independent framebuffer checkpoint. Carry
   over source/binary pins, but build a new uniquely named attempt and output path.
2. Audit the native read path before adding it: PCI SMBus identity/IO enable/BAR,
   entry status, bounded transaction outcome and final status. Keep all refusal
   conditions. Do not clear unknown inherited pending bits, borrow firmware state,
   write an encoder recipe or turn a rejected read into success. A protocol read
   may require audited controller command writes; distinguish those from encoder
   configuration. Start with the smallest useful read, not a Windows boot.
3. Show phase and refusal/result codes directly through the admitted framebuffer,
   independent of SMBus LED writes. Keep a distinct transition-success indication
   so a subsequent read failure cannot hide the successful handoff. Ensure result
   presentation is persistent and understandable before requesting watched hardware.
4. Prove code/data/stack/table extents and full actual compiled transition in new
   host fixtures, including native read negative outcomes and bounded timeouts.
   Host IO models are not physical bus proof. Preserve failures. Any context in
   files before transfer remains pre-write; do not relabel it as native capture.
5. Acquire fresh watch/reset availability for the new deliberate hold; stage exact
   bytes and send one bounded SITE request. Never retry an uncertain launch. After
   observing and manual recovery, collect only that new attempt and audit custody.

No next candidate is implemented or staged. No startup hook or owned host process.
Build/emulator leases released; hardware ticket retained; automation paused.
Original Conexant720p and ordinary launcher untouched. Networking679,1080i and
historical boot intermittency remain tabled. Native Xcalibur initialization and
Windows1.6 video-driver work follow evidence from these reads, not kernel mode
success alone. Preserve694 build001/cpu-build001/cpu-run002 failures and all prior
closed attempts. Private assets and credentials remain outside the public repo.
