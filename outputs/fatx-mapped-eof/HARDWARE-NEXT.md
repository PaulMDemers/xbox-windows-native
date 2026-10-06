# Next physical trial: isolate FATX0098

This is a plan, not a deployment record. The console remains on FATX0088 and
video0093. Keep the new miniport/display/INF package out of the first 0098 trial,
so storage and display changes can be distinguished.

1. Read the actual dashboard state and installed payloads again. Preserve the
   original filesystem driver, startup file and relevant pre-run event logs.
   Require the known physical baseline hashes from the continuation note; retain
   the existing 0.1.0 and postrelease recovery bundles.
2. Prepare one unique owned test directory on dashboard F: (Windows C:). Stage
   the verified 0098 filesystem binary, keeping every other boot/display payload
   unchanged. Read back exact hashes. Do not copy emulator hives, synthetic PCI
   state, failed-install flags or raw FAT/directory sectors onto the console.
3. Adapt the NT5 probe to create its input files through ordinary filesystem APIs
   on hardware, then run the same boundary mapping and replacement workload.
   Deliberately dirty on-disk input slack is an emulator-only fixture property;
   the physical test must not claim to reproduce that setup without evidence.
   Exclusively create the attempt log and start once using the existing physical
   trial launch/collect convention. Preserve user files and dashboard partitions.
4. On normal dashboard return, disable the one-shot startup first, collect logs
   and exact payload/output files, decode only new event records, and run the
   established read-only physical allocation plus binary/hive audits. A popup,
   incomplete log, mismatched content, forced reboot or unavailable console is
   recorded as such and cannot silently become PASS.
5. Follow a clean bounded trial with normal desktop application saves/reopens and
   a longer soak. Promote 0098 only against those physical results. An emulator
   mapping pass does not qualify generic PnP lifetime, video acceleration or HD
   modes; those remain separate workstreams.

Expected 0098 SHA256:
`beeaf329f0446d3bdd2ed490fa8143888253115c0ff6c1662b67b82e6619eedd`

Known 0088 rollback SHA256:
`0ec6b5fdae65a1f85cba8c15021ba8095601d4462565b331329884526ff81336`
