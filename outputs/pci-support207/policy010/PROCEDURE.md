# Reproduction and evidence boundaries

This directory records a completed diagnostic, not a reusable runtime seed.
Preserve the closed veto001 fixture and original source hashes. For a new run,
copy and adapt the harness into a new attempt ID with fresh ports and a fresh
immutable seed. Do not run Continue-001.ps1 against this used directory.

1. Follow the project's xbox-native-bringup validation reference and cooperative
   build/xemu leases. Keep private disks and emulator temporary files on E.
   Preflight checks space, immutable dependencies, providers, static sites and
   harness hashes before preparation. Source pin manifests identify the exact
   kernel, drivers and emulator build.
2. Prepare under the build lease, then launch under an exclusive xemu lease.
   This run used monitor/GDB/FTP ports 4894/4895/4896, a 240-second observation
   window and a 300-second guest window. No physical or UI actions were used.
3. Match resident kernel/HID sites with image relocations before observing
   registration, interface state, notification, open, capability request,
   completion and cleanup. Record thread identity and paired entry/exit calls.
   Do not interpret callback data in an IRP work stack as an IOCTL; the outgoing
   next-stack record at policy_button_submit contains the actual request.
4. Remove breakpoints and resume before the bounded host close. Cold audit under
   the build lease. Preserve pending setup, event warnings and host-close status;
   none constitutes a successful normal Windows restart.
5. Offline review: review-static001.py, review-evidence002.py and
   review-policy002.py produce the corresponding JSON evidence. Their outputs
   use exclusive creation; compare/reproduce in an isolated new review location
   without replacing the original result files. Draft review-evidence001.py is
   the earlier strict-status reviewer and was not used for this run. The failed
   review-policy001.py and its failure record remain intact.

review-loaded-site001.py is an unexecuted, time-bounded live follow-up draft.
Its guard intentionally rejects the now-closed fixture. Do not run it now or
claim a loaded-site result. A later harness should correctly apply relocations
overlapping either edge of a pin window and preserve mismatched resident bytes.

The decisive runtime evidence is two successful capability queries returning
zero, cleanup before rebalance, and fresh HID arrivals preceding conflicting
opens. Actual power/sleep/lid event delivery and physical SMC semantics were
not exercised.
