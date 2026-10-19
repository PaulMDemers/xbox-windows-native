# Delivery-copy retention authorization

On October 19, 2026 the user reported copying the delivery to a flash drive and
explicitly authorized reclaiming the local copy if space is needed. This is a
user-reported copy; the flash drive location and its bytes have not been
independently inspected in this turn.

The authorized disposable delivery copies are:

- E:/Xbox-Test-Kits/2026-10-19/Xbox-Hardware-Info.zip
- E:/Xbox-Test-Kits/2026-10-19/Windows-2000-Xbox-E720p.zip

Their identities remain in final-artifact-identities001.json. Keep the small
checksum sidecars, START-HERE instructions, public build/evidence records and
this authorization after any later reclamation. Record the actual removed
paths and bytes when cleanup occurs. This permission does not extend to the
lossless disk archives, canonical emulator binary, backing parents, source
inputs, or recovery material retained by the previous cleanup.

No delivery files were deleted in this documentation turn: both host volumes
were above the 20 GiB reserve and the task required only small documentation
edits. The flash-drive copy and both delivered ZIPs were not modified.

Documentation now starts at docs/build-test-kits.md, linked from the README,
component build guide, build-to-boot guide and tester guides. The clean-media
converter/storage limitations remain explicit. No build or physical launch
was performed to validate prose. Next hardware work is inventory and a watched
first Windows boot on an identified target; a clarification is pending about
which console is available. Automation remains paused.
