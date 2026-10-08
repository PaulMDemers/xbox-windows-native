# Closed diagnostic: first file create succeeds

The pinned probe entry and CreateFileA execute. Actual thread/frame-paired call
creates C:\xwngdi118\result.log with handle960; raw TEB last error is0 using the
exact owned GetLastError implementation (last-error-layout.json). The probe is
therefore launched and its initial file create succeeds. Two entry E14 cases
became readable after real fault/step/re-entry, with resident-byte identity pins.

A later shared API breakpoint hit a different process and the observer's strict
probe-name assertion ended capture. It did not record that other process identity;
it does not establish the probe's own exit or reason. All breakpoints removed,
guest resumed, then explicit failed stop. No rendering cases/normal shutdown.
Cold audit has no log/refs/events; full allocation/protected/payload clean; SYSTEM
structural parse fails after forced stop, other4 hives parse. Never reuse this child.

New scanout4 records and steps through bounded non-probe hits, retaining actual
process/thread/frame pairing for the target. No driver/probe changes or gate waiver.
