# Next native Xcalibur step

684 is physically closed and685 host fixtures are closed. The incoming unit is
last known at UnleashX with HDMI. No hook or launch is pending. Networking679 and
1080i remain tabled. Do not use stale readiness for a deliberate hold/reset test.

1. Establish positive encoder presence/identity and native controller ownership.
   User identifies the board as1.6; its raw GPU/MCP fields alone are not a decoder.
   A response at0x70 is device-presence evidence, not a unique vendor/chip-ID.
   A failed Conexant/Focus read is not positive Xcalibur evidence.
2. Integrate the new binding into a fresh pinned native source tree. Validate
   actual pre-write CPU/interrupt/port context and timer behavior there. Kernel
   snapshot684 is not a substitute for that handoff. Stop on dirty/busy status;
   do not clear unknown pending work or change IF merely to satisfy a gate.
3. Preserve exact source-derived GPU setup, NTSC/HDTV/480p admission and the
   64MiB/55MiB/9MiB/316160 allocation contract. Add exact failed-register and
   phase reporting around table programming. Keep the maintained Conexant path
   and its manifest unchanged until a separate profile is qualified.
4. Validate compiled full-image paths and every bounded failure exit. The first
   native encoder trial must be a separate watched pattern-only run with reset
   availability. It must not start Windows. Verify colors, geometry and stability.
5. Only then prepare a separately pinned Windows480p handoff/input/persistence
   test. Kernel720p baseline683 does not qualify native720p or live mode switching.

One source lead for the identification review is the primary
[YeloDebug implementation](https://github.com/smx-smx/open-sauce/blob/master/Xbox/Xbox1/YeloDebug/Xbox.cs),
which explicitly probes the Xcalibur address through the kernel SMBus service.
Its probe semantics/constants and behavior on this target still need review;
no code from it was copied or executed. Do not borrow its broader memory/EEPROM
inspection behavior. A kernel-service read also does not validate native block I/O.
