#647 prepared/staged: post-video-result diagnostic, no launch yet

This diagnostic derives from exact633 source tree
70c0a6c5aff82537f489e7d18410d5980fa797a7. It adds an LED indication only AFTER
xwn_hd_apply returns, followed by the original success or fail/reset logic.
No video profile, memory reservation, hardware-validation predicate, timeout,
interrupt setup or functional reset logic was changed. Removing the two source
insertions recovers the original native wrapper exactly. The adapter object text
and profile object text/rodata also match633 byte-for-byte before linking.

The indicator sets SMC LED pattern/control through the existing bounded SMBus
writer, waits eight one-second delay calls, then requests automatic LED control.
It does not retry failed LED transactions. Its status remains in diagnostic RAM;
there is no durable guest receipt. Timing and SMC state are perturbed, and code
layout changes, so a successful run would not establish an ordinary-boot fix.

| Observed indication for about eight seconds | Candidate interpretation |
|---|---|
| Green/off flashing | Video setup returned success, stage5/error0 |
| Red/off flashing | Configuration rejected before adapter writes |
| Red/amber alternating | Encoder SMBus transaction failed |
| Solid amber | Synchronization poll timed out |
| Red/green alternating | Vertical-blank poll timed out |
| Green/amber alternating | Geometry, pitch or format readback mismatch |
| No distinct indication | Inconclusive: earlier exit, signaling failure, missed interval or unexpected state |

After a failure indication the original reset path is taken. After success it
continues toward Windows; later failure remains possible. LED observation alone
does not attest exact instructions, hardware register values or successful Windows
startup. The diagnostic does not identify a prior run's cause retroactively.

Build001 compiled and passed70 host checks but was rejected in review because
solid red/green overlapped ordinary boot indicators. Its sources are preserved
under candidate001 and its private outputs remain intact. Build002 failed before
compilation because a derived script incorrectly changed the pinned parent path;
build002.json and its script retain the failure. Build003 corrects that path and
uses the distinct flashing patterns. No earlier candidate was staged/launched.

Build003: GCC12 pinned SHA, flags identical to633 including mode3; source tree
and outputs in build003.json.70 ASan/UBSan host checks pass.56 cases execute the
actual compiled wrapper with explicit models for video-setup return, SMBus writes
and delay, while running the actual profile selection code. They cover each result
class and each failed diagnostic write, ABI return preservation and unchanged
original reset path. These are not physical timing, LED or Windows proof.

Private candidate C:/xwn647/build003/default.xbe is301584 bytes, SHA256
9c62cd343a6236363716a395e740f890de83b8a05d0bf5c8be9b1ca3f0b899b4.
New source/object/temp/output files live on C. The build checks output and WSL
backing volumes with a20.02GiB threshold; no VM, disk or backing chain was created,
moved or deleted. Existing build lease was acquired and released for each build.

Physical preparation captured28 selected files and confirmed ordinary720p plus
normal startup. Staging wrote only the unique E:/Applications/XWNVideo647 folder,
owner.json and default.xbe, with exact readback. No startup hook or XboxC access.
The ordinary720p launcher remains unchanged. All host processes exited. No SITE
has been sent. User watch readiness is pending. Do not launch without the specific
LED/screen observation being available; see NEXT.md.645/646 remain closed.
