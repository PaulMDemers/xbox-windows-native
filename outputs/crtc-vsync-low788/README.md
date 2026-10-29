# CR10 vertical-sync-start low-byte control788

Kernel-context diagnostic, not a video driver or full mode switch. See NEXT.md
and source-review001.json for evidence and limits. Built with pinned nxdk via
build.py under the shared build lease. model.py, layout_model.py and clock_model.py
require the shared xemu lease and XBOX_XEMU_MODE=exclusive; they execute owned
compiled object fragments, never a closed runtime. No proprietary binary is public.

614 fault outcomes include 39 new CR10 baseline/readback/neighbor/recovery cases,
all 575 prior cases, exact reverse ordering and cross-transaction corruption.
Source/build hashes, linked-byte checks and strict schema mutations gate staging.
Physical controller requires private active connection.json; no credentials here.
One accepted or uncertain SITE is never repeated. Dashboard return requires fresh
seven-record collection and audit, not just FTP or a green color.
