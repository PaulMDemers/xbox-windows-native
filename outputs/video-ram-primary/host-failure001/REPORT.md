# Preserved host shim failure

Owned Linux root: /home/paul/xbox-windows-native/build/video-ram-primary-host001.
The actual surface/shadow source, shim, test body and binary remain there.
This directory retains the original generated shim/stubs/calls and test body.

The test aborted in engine-stubs.inc:133 at EngStretchBlt's psoMask==NULL
assertion. The generator globally replaced prior mask assertions while adding
StretchBltROP. StretchBlt's valid mask should have compared with ExpectedOther.
The fix applies that replacement only to the current ROP callback body. No
driver change followed this failure. Fresh host002 passed46 cases and65,536
dependency truth tables with ASan/UBSan and leak detection. No guest was involved.
