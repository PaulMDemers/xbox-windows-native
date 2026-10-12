#310 explicit HD profiles implemented, not yet integrated

Pure C profile selection now supplies720p and1080i geometry,35 CRTC values,28 MMIO values and14 encoder programming values. It refuses unsupported modes and changed64MiB/55MiB/9MiB/316160-byte memory contracts; invalid selections leave output untouched. No hardware I/O, loader build or deployment occurs in310.

The compiled host implementation passes92 checks under ASan/UBSan. Independent review agrees with the owned pinned4034 programming facts and102 applicable fields from physical309;1512 single-bit mutations of claimed reading fields are rejected. For CRTC19 only pitch bits[e0] are compared; for2d only horizontal-extension bit[01]. Other differing bits remain recorded and unexplained, not asserted read-only. Twelve CRTC fields and13 MMIO fields are static-only, not hardware readback claims.6c programming value46 is distinct from observed0; raw0 is never replayed.

Source review identifies a concrete integration difference: existing Cromwell Conexant setup clears680630/68084c/6808c4, while the selected stockHD profiles require3/00801080/40801080. It also derives sync end values heuristically instead of using measured timings. Correcting resolution selection alone is insufficient. The stock setter retains VPLL680508 rather than programming its observed value.

Next is actual ordered programming integration and review, starting720p, with bounded failure/recovery behavior. No native WindowsHD, GPU acceleration, physical promotion or0.2.0 claim. Header/compiler sources and private host executable are pinned; shared SDK/loader sources unchanged.
