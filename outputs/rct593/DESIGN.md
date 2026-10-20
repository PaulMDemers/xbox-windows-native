# RCT593 bounded save visibility observation

Followup to physical592: immediately after dialog closure the helper received
ERROR_FILE_NOT_FOUND, but a new save survived normal restart. This does not prove
the cause. Add a30second bounded observation, never resubmit Save. Retry only
missing-file/sharing/lock observations; fatal other errors fail. Open without
write-sharing, hash wholefile with SHA1, demand matching bytes/hash in at least
three complete reads across1000ms, then capture the park. Stable observation is
not proof of durable storage or successful reload; still require cold readback,
normal shutdown and later Load. Timing starts after Save dialog closes.

Fresh593 namespace and PC fixture from immutable404; never reuse closed disks.
No Xbox launch until native PC test and cleanup audits qualify. Earlier failure
592 stays failed. Host reserve blocks VM admission until restored. No functional
driver/game change, no fullscreen/sound/boot investigation, no GPU/FPS claim.
