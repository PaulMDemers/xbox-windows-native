# 498 host-only early-entry gate passes; no console change

host001 completed 199 actual i386 assembly executions: 128 register/flag cases and
71 modeled file-failure/cleanup cases. Each also attempted reentry and refused it
without overwriting the first record or repeating I/O. The independent decoder
rejected 1,019 malformed/truncated/checksum/semantic transports. All child processes
exited; 606 private host artifacts are retained under C:/xwn498/host001.

The proposed entry gate preserves the original general registers, ESP and flags,
writes an exclusive early receipt, and continues only after successful write,
flush and close checks. Failure follows a one-shot refusal path. The actual NT
file and firmware services are host models. Ring0 context, physical file writes,
boot success and D3D capability are not qualified. No XBE was built or installed,
no guest/console launched, no SDK/shared source changed and no new hook created.

A complete entry receipt does not prove the final flush/close returned: bytes can
exist before either fails. Tests retain this distinction, and decode never reports
Windows/preparation/graphics success. Missing entry.bin remains ambiguous without
independent evidence. Early I/O also changes timing and allocation/cache conditions;
it must not be promoted as an ordinary boot fix.

497 remains CLOSED with no entry/Windows result; its protected files/hives/events
were unchanged and its hook removed. It is pushed as 8935db5a. The user screen
question remains pending. 496 PC combined XYZ/texture/depth PASS is unchanged;
Xbox combined-scene qualification is still absent. No identical hardware retry.

One authoring typo initially added a literal backtick-n before the new .gitattributes
pattern. It was corrected before staging; no executed test source was changed.
No host compile/test failure occurred. Compiler/tool hashes in host001 are postbuild
pins, not a complete prebuild dependency closure; require that for an actual XBE.
