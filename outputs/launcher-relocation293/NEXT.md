# Relocation milestone

The matching fresh runtime control/candidate295 reached entry and BootFromDevice with exact resident instructions, expected relocated ESP and unchanged video state. Do not relaunch them. Next needs a fresh fixture containing the matching Windows boot payload to verify FreeLdr, kernel and normal shutdown before physical launcher replacement. Retain the installed original as rollback. Do not treat blank-fixture checkpoints as a Windows boot.

After that, define and review one coordinated 9 MiB reservation across launcher memory map, FreeLdr, bootvid, permanent provider and miniport. Complete CRTC interlace/PLL/encoder state is still required before programming 1080i; 292 FP captures alone are insufficient. No 0.2.0 tag yet.
