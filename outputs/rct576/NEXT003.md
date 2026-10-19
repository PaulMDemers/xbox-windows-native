# Physical576 stage recovery002 ACTIVE

Original stage001 failed10:34:35UTC on the final FTP reply to an APPE. It is
immutable and preserved with supervisor001-stage and stage-failure001. No hook
or launch occurred. Read-only probe002 independently read2785280bytes from the
partial Css9.dat twice; both match the expected prefix of7005802bytes. The old
progress counter was2129920, which is deliberately not used as a resume offset.

Recovery-admission002 freezes new sources and failure/probe records. Seven resume
fault tests and twelve controller launch/collection tests passed. The fresh
stage002 verifies directory ownership/inventory, all previous bytes and baseline,
then appends from the exact observed prefix and adds only missing files. It never
repeats the uncertain append. Startup hook remains LAST. Active exec61471,
supervisor002-stage,1200-second host bound; read actual journals for completion.

On success use C:/xwn576/session.py outputs/rct576/supervise002.py launch ONCE.
This invokes controller002 and stage002, not the failed stage001 controller.
Then the same private wrapper with observe001.py makes a600-second read-only
dashboard observation. Never repeat an accepted or uncertain SITE request.
On return use supervise002.py collect: hook FIRST. First cold audit is audit002.py
1 under WSL/libhivex; registry_review002.py runs on the Windows host. Follow with
capture_review001.py (bundled Pillow) and review001.py (host), independent visual
inspection, and an exact final record. Do not use audit001 or registry_review001,
which bind the failed stage. If another transfer failure occurs, preserve it;
do not rerun either stage journal or launch incomplete assets.

PC578 CLOSED and pushed7001173b; its Save dialog result is not an Xbox result.
Next PC persistence plan is578/NEXT.md. No new PC fixture is admitted yet.
Deadline14:00UTC Oct19, closeout13:50; no user reset available before10am.
