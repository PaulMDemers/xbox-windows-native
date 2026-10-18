#539: a previously hidden diagnostic difference isolated

The ordinary374 and recorder490 Xromwell payloads share their original code,
except for five bytes at stack setup. The recorder detours through a574-byte
LED/SMBus diagnostic. It also has235972 padding bytes, extending the initialized
payload from288316 to524862 bytes. Both request1MiB. These differences, plus the
recorder's allocation guards and earlier file IO, mean536's two successful boots
cannot establish ordinary-launcher reliability or a CPU-state cause.

Candidate539b restores the five original MOV ESP instruction bytes while retaining
the recorder's size, addresses, longer copy and earlier instrumentation. It removes
execution of the added post-stack LED diagnostic, including its failure halt;
it does not invent a success result or change a functional driver. The section
digest and four same-length path strings are updated. The inactive tail remains.
Candidate539a is an offline control, not a scheduled physical run.

Host results:

- Ten exact-prefix cases passed with modeled kernel allocations/results and DF
  injection. Normal allocation requests are equivalent after dereferencing the
  actual argument pointers. Under the injected failures the diagnostic refuses
  before reporting; the ordinary prefix reaches unmapped modeled memory. This
  does not establish that any injected condition occurred on the Xbox.
- Forty exact stack-boundary cases passed. The control's modeled SMBus success,
  busy, error and deadline paths behaved as specified. The restored candidate
  reaches the original continuation in one instruction with no added port IO.
- Nineteen controller admission/launch/receipt cases and six stage/capture cases
  passed with modeled FTP. The single-launch journal rejects retry after either
  an accepted or uncertain request. Compatible decoders reproduce both retained
  closed536 results offline; no closed runtime was recollected.

Failures retained: prefix-host001 compared pointer addresses instead of referents;
prefix-host002 corrected the comparison. workflow001 failed on a redundant string
replacement after producing two local files; workflow002 verified those unchanged
files and completed the rest. The subsequent missing-test-script invocations are
recorded with that failure. Neither failure touched the console.

At20:16:02UTC the bounded stage supervisor closed successfully. Only the new
/E/Applications/XWNBoot539b folder, owner.json and default.xbe were written and
read back. Protected720p and ordinary launcher/startup checks passed before and
after staging. No hook was installed; Xbox C was not accessed. No launch or
Windows result exists yet. The pending readiness question asks whether the Xbox
has stayed powered at UnleashX since536, with no intervening launch/power cycle.

See DESIGN.md for the one-run inference limits and NEXT.md for the exact workflow.
Boot reliability, D3D/GPU/game and release claims remain unchanged. Automation is
paused; this work follows the user's later manual authorization.

## Single launch sent

User confirmed uninterrupted dashboard power since536. The fresh before1 capture
completed20:34:13UTC and all ten selected files equal retained536 after2. One539b
SITE launch was sent; its bounded host supervisor closed successfully20:34:52UTC.
The screen observation is pending. No second launch or retry is admitted. No hook
was installed. Host completion does not establish Windows execution or shutdown.

## Closed result: dashboard return without a watched boot

The user was elsewhere and can confirm only that the console is at the dashboard.
No Windows desktop, reset path or normal shutdown was observed. The one fresh
after1 collection completed20:38:49UTC. All ten baseline files are byte-identical;
all five registry hives pass their checks. Neither Windows event log nor video
trace changed. There are no new6005/6006 events and no normal-shutdown delta.

All three diagnostic packets are valid and there is no refusal packet. The primary
preparation packet is byte-identical to both successful536 cases. All recorded
control registers, flags, segments, descriptor-table pointers, stack and return
addresses match at corresponding epochs. Only TSC values and preceding LED poll
counts differ (1155 versus1170/1158). This proves progress through the recorded
pre-handoff checkpoints, not execution of the restored stack instruction.

The result does not qualify a Windows boot, identify where it stopped, or prove
that the removed post-stack LED hook was necessary. It remains one unobserved
return with no persisted Windows activity. No identical retry or second control
launch was made. Ordinary720p/startup remain exact, no hook was installed and all
owned supervisors are closed. The console is authenticated at the dashboard.
See final001.json and NEXT-CLOSED.md; the original NEXT.md is historical.
