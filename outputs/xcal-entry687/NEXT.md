# Next: separate native Xcalibur pattern integration

686 physical and687 host fixtures are CLOSED. Last console observation is the
incoming1.6 at the dashboard with HDMI after686 collection. No hook or launch is
pending. Keep networking679, 1080i and boot intermittency tabled. The original
development console's720p package and all maintained launcher pins are unchanged.

1. Use retained source tree `70c0a6c5aff82537f489e7d18410d5980fa797a7` and a fresh
   owned build to add a separate pattern-only path before
   `BootEepromReadEntireEEPROM`. Review earlier startup transactions too: moving
   before the EEPROM call alone does not prove exclusive bus ownership. Do not
   globally patch the legacy reader or weaken the dirty-status gate.
2. Capture actual entry CPU/IF, controller and timer context before writes. Use
   the checked cable/video readers and explicit positive Xcalibur observation;
   refuse unsupported/ambiguous context. Keep kernel686 presence evidence
   distinct from native block-read qualification. Do not borrow kernel GPU state,
   clear unknown pending status or change IF solely to satisfy admission.
3. Review source-derived GPU clock/output/stride/geometry setup and the exact
   NTSC/HDTV/480p table. The existing legacy geometry function does not itself
   program the PLL or framebuffer start. Legacy `NVVertIntrEnabled(...,0)` still
   enables interrupt bits: do not copy that behavior blindly. Keep the reviewed
   64MiB/55MiB/9MiB/316160 memory contract and default Conexant path intact.
4. Add bounded phase/failing-register reporting and failure exits. Validate the
   compiled full-image paths before any console launch; host models do not
   establish physical timing, controller ownership or a visible pattern.
5. Prepare a separate watched pattern-only native trial, with fresh confirmation
   that the user can observe and reset any deliberate hold. Do not start Windows.
   Only after visible colors/geometry/stability and exact records qualify that
   path should a separately pinned Windows480p handoff/input/persistence test follow.

Use fresh IDs, exact source/binary pins, the existing build/hardware leases,
capacity checks and one SITE request with a20-second reply bound. Never retry an
accepted/uncertain launch or reopen a closed runtime. Preserve failed evidence.
Only owned E/F paths are eligible; dashboard C is off limits. No hidden startup
hook or reset request is outstanding now. Hardware ticket retained; automation
paused. There is no native720p/live-mode-switch or Windows1.6 qualification yet.
