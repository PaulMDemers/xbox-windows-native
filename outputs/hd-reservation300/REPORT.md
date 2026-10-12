# Nine-MiB reservation candidate compiled and host-tested

Matched control001/candidate001 compiled FreeLdr, rosload, bootvid, miniport and the relocated Cromwell XBE. Both retain the existing low-resolution timing code. Candidate has the version2 nine-MiB reservation; control retains version1 four-MiB. Binary review confirms matching import/export interfaces, actual reservation constants, relocated startup/copy instructions and over1.7MiB stack headroom. Both builds report the same33 warning messages; no new warning or clock-skew message appeared.

Actual provider/layout host code passed37311 assertions plus40000 concurrent acquire/release attempts under ASan/UBSan. Cases reject legacy descriptor versions/sizes, wrong physical ranges, guard overlap, malformed multiboot entries, geometry overflow and invalid ownership. NT locks/IRQL are modeled: these results are not physical mapping or Windows runtime proof.

Preparation001 stopped at an ambiguous LoadReactOS edit anchor before compilation. Its script, report and partial source snapshots remain preserved. Completion002 used the unique startReactOS context and generated pinned patches. A subsequent build preflight refused projected C capacity before any build output; verified closed portable archives recovered space, then build001 ran. No consumed build or guest attempt was repeated.

Archival299 moved13 closed non-backing portable copies with full hash readback and original-path junctions;299c moved6 more.299b refused a historical run whose resolved path was outside its declared C workspace boundary before any mutation. No existing disk backing chain moved. New runtime301 fixtures use an empty healthy D volume instead of consuming the limited remaining C/E space.

No physical file, Windows driver, SDK or shared source checkout changed. No1080i or0.2.0 qualification. See the separate301 ordinary emulator results when closed; compilation alone does not authorize a PASS for runtime reservation/alias checks.
