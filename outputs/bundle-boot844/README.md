# 1.6 fixed 720p XWNEBoot reconstruction

This source-only reconstruction starts from the closed 843 source trees, verifies their recorded Git tree IDs, and changes the application directory in Xromwell and FreeLoader and makes the wrapper status report reusable to `E:\Applications\XWNEBoot`. The Windows installation remains on E and the 843 boot-loaded FATX override remains distinct from the installed Windows driver. No console was accessed. The new path-adjusted binaries have not been physically booted; 843 itself reached the desktop with a preconnected mouse, but shutdown stalled and persistence is unqualified.

Run records: `source001.json`, `chain001.json`, `host001.json`, `qualify001.json`, `report-test001.json`, and `xbe003.json`. The first XBE attempt, `xbe001.json`, stopped before make because host metadata omitted Makefile; `xbe002.py` checks its 843 build pin instead. Both records are retained. Builds used the shared build lease. Source and NT5 build live privately at `/home/paul/xbox-windows-native/bundle-boot844-source001`; binaries and logs are under `D:/xwn-bundle844`. Build-space preflight checked 23 GiB on WSL and its Windows backing volume.

- `D:/xwn-bundle844/xbe003/bin/default.xbe`: SHA-256 `099c540a91ab1c0975f084fc92ebf9ae58171b12a1f8eb339d28cd9b5a40b4d2`.
- `D:/xwn-bundle844/chain001/freeldr.sys`: `721cf348903138773854b3dd3dce336cb660610d8d85673f3105d8c26aa13d9e`.
- `D:/xwn-bundle844/chain001/rosload.exe`: `c78576199f6cb9effdfd736b787614ce19dd023d2066509104364816443dc687`.
- `C:/xwn843/driver003/xwnfatx.sys`: `3b2179ecec681cd91bc910a6178956d660f7bac18aa69bf6eafdb9f483a9af2c`; the previously built and tested 843 boot-loaded driver, not a fresh driver build.

The wrapper overwrites and verifies one bounded `E:\Applications\XWNEBoot\boot-report.json` at each checkpoint. A host-substituted file API test passed 150 consecutive calls. The host tests exercised 37 bridge/page cases, 14 retained-mode logic cases, 14 64 MiB map cases, and the compiled call path. These checks do not prove physical boot. The 1.6 kernel patterns for other modes are not evidence of Windows support.

