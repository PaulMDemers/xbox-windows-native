# Physical codec boundary

The preserved physical v2 probe (`native-windows-hardware-probe-v2`, input hash
43c7f4ec49b1731fb5d6f369f6bc2d654c726a11a3a444f7f271ce506838d749)
records ACI PCI00:06.0, 10DE:01B1, BARs D001/D201/FEC00000, IRQ6. This is distinct
from APU00:05.0, 10DE:01B0, FE800000, IRQ5. The later NT5 registry pins are in
inventory001.json. Do not infer the physical codec's ID from xemu's codec.

Build004 implements the following preparation for a physical trial. Ordinary
xemu installation and two subsequent playback boots pass, but actual physical
codec behavior still requires coordinator-controlled validation:

1. Accept the real ACI translated resource shape (two I/O ranges plus MMIO and
   one IRQ), while accessing only the validated MMIO aperture. Keep exact01B1 INF.
2. Identify the codec through real vendor ID reads after bounded link readiness.
   WM9709's vendor-authored datasheet lists 574D/4C09; nxdk describes its fixed
   interface. A physical ID mismatch must fail explicitly, not use cached PC data.
3. A fixed stereo48k render topology without nonexistent capture/mixer controls.
   Do not acknowledge master-volume writes that cannot alter the signal. WDM
   software mixing remains Microsoft's ordinary audio path.
4. Quiesce firmware-inherited PCM/S/PDIF DMA before publishing a new ring. Retain
   allocations on unconfirmed halt; bound every reset/readiness wait. PCM output
   alone does not prove S/PDIF/HDMI-adapter playback.
5. Exact-code host fault tests for both resource shapes, unknown codec rejection,
   readiness failure and cleanup, followed by ordinary xemu regression. A mocked
   Wolfson response is only a host test, never physical or ordinary-xemu proof.

The user's output-connection preference was requested asynchronously. Initial
work continues on analog stereo PCM; digital-output behavior is not established
by the retained evidence. The experimental package is ready for coordinator review, with no physical
qualification claim. Its final WaveCyclic filter has two pins and one actual DAC
node, and no separate topology filter. This avoids the node-less graph associated
with the retained SysAudio crash in build003.
