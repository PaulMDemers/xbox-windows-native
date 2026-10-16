# Working-demo comparison 415

The live physical demo still matches the protected code and normal startup
recorded in411. The clean403/405/406 rebuild was not deployed over it. Successful
File Explorer launch and failed menu/FTP observations used the same installed
version, but different launch routes. Same-build, same-route, same-start-state
intermittency has not been established. The physical launch failure remains
unexplained; no binary regression or keyboard cause is inferred.

415 performed one read-only FTP capture of31 selected E files, then extracted34
selected files from the already closed406 disk. Protected live files matched411;
the406 disk hash was unchanged before/after extraction and each extracted file
matched its prior cold inventory. No Xbox C access, physical write, reboot,
emulator launch, build, SDK change or release tag occurred. Private files are
under E:/xwn415. They are not redistribution assets.

## Actual differences

| Component | Result |
| --- | --- |
| Launcher XBE | Same300624 bytes;20 section-digest bytes and one displayed date byte differ. Both section digests validate. Wrapper and Cromwell instruction ranges are exact. |
| FATX, video miniport, display DLL, network, ownership and audio | Complete files differ only in PE COFF/export timestamps and checksum. All other bytes exact. |
|16 selected Microsoft system/player files | Byte-identical, including kernel, win32k, setup/input support libraries and WMP executable. This is a selected-file comparison, not complete Windows installation equivalence. |
| HAL |12765 bytes differ; not metadata-only.235 changed instruction operands point to identical strings; two point to different build-source paths.206 changed instruction/data spans remain unclassified. |
| FreeLoader |4475 bytes differ; not metadata-only. Its executable section also contains strings/data, so2153 unclassified disassembly spans are NOT2153 demonstrated instruction changes. |
| ROS loader |147 bytes differ. Two changed code operands point to identical strings; data includes different build-source roots. Full equivalence remains unproved. |

The previously qualified403 canonical-path HAL reconstruction is a DIFFERENT
artifact from the fresh compiler HAL used in406. Its historical metadata-only
match must not be applied to the fresh HAL. Diagnostic source-root spelling and
length are a demonstrated reproducibility issue; that is not proof that every
remaining fresh-build difference is harmless.

The classifier rejects74 actual-file controls, including code/data, entrypoint
and length changes, and modified XBE instructions even after recomputing valid
section digests. Instruction analysis is conservative byte classification, not
a behavioral-equivalence test. Sources and original results remain preserved.

## Configuration and state

The demo FreeLoader configuration has Display/MinimalUI=Yes; the fresh one omits
it. Both select timeout0 and the same XwnProbe token. The demo has a marker-gated
outline-dragging startup helper; the fresh install has no such startup script.
Neither difference establishes a pre-Xromwell launch failure.

Selected active-control-set comparison found:

- Demo HidServ service registration is present; fresh registration is absent.
  The fresh inventory contains hidserv.exe and its INF, so this is a setup/state
  difference, not evidence that the executable is missing.
- AutoReboot is0 in the demo and1 in the fresh install.
- Six service ImagePath values have identical text but REG_SZ versus
  REG_EXPAND_SZ types. Other selected start/type/group and critical input/PCI
  bindings and C mount bytes match.
- XboxVnt5 Device0 stores640x480 defaults in the demo and1280x720 in the fresh
  install. These stored values do not establish the effective mode: the working
  demo was observed at720p. No live mode change occurred.

SYSTEM/SOFTWARE hive hashes naturally differ. This selected read-only review
does not claim complete PnP, display-profile or registry parity. The first hive
reader invocation failed to load libhivex before opening a hive; the exact
unchanged script then succeeded with the existing dependency directory in its
process-local loader path. Original failure is retained.

## Next decision

Preserve E:/Applications/XWNEBoot/default.xbe as the known working File Explorer
route and C:/xwndemo407/play.cmd as the demo. Do not substitute FTP SITE launch
and call it a matched File Explorer test. Do not replace the demo wholesale.

Finish source/toolchain/path classification of the three loader components,
then prepare a separate staged candidate using the same configuration and
Windows files. A physical comparison must use the same direct File Explorer
route, record starting state and actual screen transitions, and vary one
reviewed component group at a time. A separate menu-route investigation should
compare the SAME executable/configuration, not a newer complete installation.

Clean-install FATX long-name exclusions and strict event failures are separate
release blockers. Six genuine over42-byte FATX names remain unresolved; no
security/state files may be silently dropped, renamed or truncated. This
comparison does not qualify a clean physical install or public release.
