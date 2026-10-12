# Coordinated Windows HD handoff is next

1. Preserve physical288 and standalone289/290 evidence. Do not repeat the solved
   standalone pixel-only test. Current connection is STANDARD AV, not component.
   Obtain component/HDTV-capable Xbox output plus a1080i-capable display for later
   physical trials; do not force the current adapter or alter physical EEPROM.
2. Review/pin the complete Cromwell live-memory map and a separate reversible HD
   boot profile. Current code at58MiB and stack below60MiB overlap any naive enlarged
   top-RAM framebuffer. The observed standalone1080 allocation starts58,683,392,
   below current Cromwell code. The kernel allocator result is NOT a native launcher
   allocation authority. Preserve original recovery launcher/Windows entry.
3. Specify a shared layout with at least8,294,400 pixel bytes plus bootvid's316,160
   backing bytes (already exceeds8MiB) and explicit alignment/other owners. Coordinate
   multiboot reservation, FreeLdr, bootvid/provider, miniport and software display;
   include64MiB working-memory pressure. Review128MiB behavior separately.
4. Review Conexant encoder plus NV2A timing/stride/interlace state as one transition.
   Current Cromwell HDTV path selects480p; Xcalibur helper ignores HD selection.
   Use actual source/encoder validation, refuse unsupported combinations. Runtime
   fallback HVALID719 for640 pixels proves why timing width alone is insufficient.
5. Build isolated components and verify exact framebuffer/handoff bounds in fresh
   emulator children, then prepare a bounded physical trial with rollback and logs.
   Tag/bundle0.2.0 only when agreed1080i behavior is stable. Acceleration/disposal287
   remains deferred; standalone mode success is not Windows HD readiness.
