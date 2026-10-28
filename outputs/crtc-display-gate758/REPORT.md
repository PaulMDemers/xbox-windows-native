# Kernel758 staged: CR17 bit7 clear and own-byte recovery

After closed kernel756/native757 qualification, extend only the next original
CR17 read/modify/write. Capture the fresh byte, require it still equals the
qualified prefix readback, clear bit7 only, then check CR00/02/03/04/05 neighbors.
Restore CR17 to its own saved full byte first, then reverse prior qualified
writes. A CR17 recovery mismatch inhibits output and requests firmware restart.
No new CR01/02 target writes, final display-enable write, pitch/vertical changes,
encoder/PLL changes, native handoff or Windows boot is included.

Host checks pass:169 actual-COFF transaction cases,2353 layout cases,10 actual
clock-gate cases, exact linked bytes, independent source/schema validation and
mutation checks. The164-word656-byte record includes eleven distinct CR17-phase
fields. Existing native placement would end5390 inside5400, but no native
candidate is built or qualified here. Clock3375000/high0 gate remains unchanged.

Initial model001 failed because its before-read fault also affected final prefix
readback. The failure and model.py are retained. Fresh model002 narrows that
fault to pre-recovery; the build is unchanged. No physical failure is implied.

Source/index and private build pins match. Unique E stage/readback passed.
No launch or hook yet. Existing bounded automatic-return authorization applies.
After a single accepted/uncertain SITE, never retry; observe dashboard for a
bounded interval, collect once and independently audit. No full mode claim.
