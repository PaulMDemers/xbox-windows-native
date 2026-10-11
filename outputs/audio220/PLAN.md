# Bounded audio hardware trial

The October10 hardware220 authorization supersedes the old audio207 coordinator-
only restriction. Audio owns the persistent ticket before all physical access.
Use only the already reviewed build004 package; no exploratory register pokes,
HAL/video change, device disabling or event suppression.

1. Fresh actual baseline capture, including all five hives/companions, all INF
   files, boot/startup/protected components and current audio driver bytes.
2. Leased cold hive and binding audit, actual physical helper-library hashes and
   actual Xbox HAL/native driver export validation. Verify source and payload pins.
3. Match the tested emulator installation starting conditions. The emulator trial
   upgraded the old bound ac97xnt5.sys file to build004 before boot, without editing
   its service/device binding. Whether that exact preparation applies physically
   is gated on the captured live installation's cold ACI binding. Do not silently
   substitute a different installation route or waive an ACI wizard prompt.
4. One recorded Windows installation launch, joined known-wizard helper and actual
   SetupAPI installation, real idle checks and unforced restart. Observe up to600s;
   a timeout never permits another launch. Restore normal startup on return before
   collection. Preserve all logs/hives/INF/driver state and event history.
5. One validated read-only F allocation scan, with new E-only app/report paths.
   Require cold/runtime installation gates before a subsequent playback boot.
6. One subsequent Windows playback launch without reinstall or binding edits;
   twelve cycles and exact device/module/progress checks. Audible output is a
   separate user observation, not a prerequisite for driver/log-only results.
   Preserve evidence and run the read-only allocation scan.
7. Restore captured incoming startup, consistent hive/companion set, INF state and
   audio files. Remove only exact newly introduced files identified by snapshots
   and preserved post-trial hashes. Preserve event/setup history, failed bytes and
   unique inactive trial directories. Verify file readback and final allocation.
8. Confirm dashboard ownership, no active physical process and restored baseline,
   then close the queue with the final report path. Review/commit/push on the audio
   branch only. No canonical source edits or video candidate deployment.

Original0088/immutable0.1.0 are never changed. Ftdisk49 remains a strict whole-boot
failure even if scoped driver/runtime gates pass. Physical codec behavior and
audibility remain unqualified until directly supported by the trial's evidence.
