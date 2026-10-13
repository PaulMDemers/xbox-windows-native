# E-specific resolution configuration

The fresh720p Cromwell build starts from pinned311 tree
0c91ebed7809d186f328c0b8cc30f612df0cfc7d and changes only two XWNFBoot loader-path
strings to XWNEBoot. HD reservation and720p timing flags remain explicit.
Build001 SHA6240a801d97c4894e56d516a934059da056446fb77cf895b5364bdd6cd24be9a
passes relocated layout, stack headroom, path and inherited-warning review.
The first wrapper attempt refused an occupied build lease before creating source
or output; the build ran only after373 closed. No shared source was modified.

The new tools/configure-e-display.py checks all five shared prerequisites and a
recognized current launcher. It only reads the six allowlisted dashboard E
files and only writes default.xbe. It preserves a fresh local rollback receipt,
rechecks before mutation, verifies readback, and attempts rollback on a failed
write. No launch API is present. Ten modeled-FTP tests execute its actual code,
including wrong inputs, wrong partitions, interrupted write and corrupted
rollback. Real read-only inspection matched the current physical1080i setup.

Actual720p boot qualification is separate in377. No physical720p profile change
has been made by this kit. Existing F overlay tools and immutable tags remain
unchanged. A selected mode is not a guarantee for every encoder/HDMI adapter.
