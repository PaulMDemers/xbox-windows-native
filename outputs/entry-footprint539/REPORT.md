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
