# PC607: absent CreateDIBSection output qualified

The original Windows 2000 control passed both pristine and traced execution with
identical subject logs. Successful RGB and BI_BITFIELDS bitmap creation with a
NULL ppvBits argument returned objects whose dimensions and bit depth were checked
through GetObjectA; both were deleted. An invalid header with the same absent
output failed as expected. This validates the observed NT5 behavior, not a promise
that every Windows implementation accepts the argument.

The recorder change only emits OUTPUT_ABSENT for that NULL CreateDIBSection output
address. It preserves the actual return value and invents no bits pointer.
Non-NULL output read failures and DirectDraw interface/output checks remain strict.
BI_BITFIELDS is still reported as unsupported by the bounded header decoder.

The independent review accepted196 paired calls,87 headers and32 StretchDIBits
samples in each phase. The prior exact graphics, failed/successful calls, recursive
two-thread control and pending/duplicate phase checks remained intact. All23
existing trace mutations,11 phase mutations and seven new absent-output mutations
were rejected. The latter cover missing/duplicate records, wrong API/address/call,
absence for a non-NULL argument and fabricated output.

Build, immutable NT5 imports, exact source inheritance and media readback passed.
The fresh404 child restarted normally at2026-10-20 04:59:13UTC, exit0. Cold
enumeration found6492 files/310 directories, unchanged tools/OS/seed, five clean
hives with independent raw-value agreement and one new6006. Raw event timestamps
support the restart; record-number order alone does not. All owned VM/build/cold
processes exited. The inherited DRM decode and incomplete allocation-audit limits
remain. Closed runtimes must never be reopened, recollected or used as parents.

No new game run or hardware change occurred in607.606 remains failed evidence.
This control permits a fresh saved-park game retry; it supplies no game costs,
FPS or Xbox acceleration result. Xbox last dashboard/no owned hook;596 SOFTWARE
cleanup remains cold-only. Launcher, protected720p, saves and transfer ZIPs are
unchanged; ZIPs exclude RCT.
