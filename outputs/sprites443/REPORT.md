# Rung04 first NT5 control: FAILED and closed

New original sample tested six default/HEL cases on Windows 2000 SP4 PC,640x480x16. No Xbox access, driver change, display-mode change or D3D/GPU claim.

- Indexed8 and RGB565: all four stages had exact source, destination, palette (indexed only), and GDI-converted bytes. Each still exited1 because cleanup detached a clipper already detached in stage2. Actual HRESULT88760238 is DDERR_NOCLIPPERATTACHED. These are not passing cases.
- RGB32 default and HEL: first keyed clipped copy returned DD_OK but16 destination pixels remained magenta instead of red. Raw source matched. Every mismatch is both red and on the rightmost column of a clip rectangle; these hypotheses are confounded. Later stages not reached.
- No whole case passed the original independent checker. No waiver or changed expected pixels. Separate failure-analysis001.json compares retained actual captures to the original oracle; final-review exact_bytes0 counts fully qualified cases only.

Build001 failed linking __chkstk_ms;002 changes only palette buffer storage and compiles warning-free,21724bytes,SHA9b8126adef59a804112dd2512264237fb47326518e5539f43417d8140508b90d.29 sample imports match owned NT5 exports. The first lease-wrapper invocation used an unsupported parameter and never launched; corrected invocation launched once.

Guest controller recorded six exits1 and requested normal restart. QEMU exited0, no timeout/host quit/kill. Cold6513files309directories,38 owned added files, five clean/raw-agreeing hives, unchanged protected binaries and source, QCOW clean, one new6006. NTFS3G independently agrees on48 selected files, unmounted with disk unchanged. Full NTFS allocation audit absent; inherited SOFTWARE DRM typed-value limitation retained.

All137 frozen/public input bytes archived privately before changing source/checker. Private outputs and failed build remain retained. No rerun/recollection/parenting of this consumed runtime. Next444 tracks clipper ownership and varies RGB colors on both axes to discriminate the mismatch; no runtime patch.
