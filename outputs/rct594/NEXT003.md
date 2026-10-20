# Physical594 bounded batched staging active

Stage001 failed PASV502 after folder move/config restore; no hook/helper/SITE.
Stage002 fresh-per-file readback was deliberately stopped by exact owned PID
before any remote writes: too slow for600s full verification. Preserve both
receipts and supervisor exits; stage-failure001/002 explain actual outcomes.

Stage003/package003/controller003 now use batch_read001: at most16files per
connection, two whole reads per file, at most two attempts only for recognized
read-only transport failures. Hash/data disagreement fails immediately. Seven
batch cases and nine recovery controller cases pass. New42 Python source files
match index exactly (staged-source-review004). Current stage session87721.

Read actual stage003/supervisor003-stage state. No launch at this checkpoint.
After stage completes, private session.py -> supervise003 launch, observe003,
supervise003 collect. Only one SITE; hook removed first on dashboard return.
Use audit004.py1 underWSL, registry_review004.py,user_hive_audit003.py,
welcome_review003.py,review_save002.py,visual-review001 then close002.py.
No code edits after package003 freeze. Old package/controller/recovery attempts
stay immutable. Observe uses explicit local module path; its prior source is
retained and final controller host tests repeated after that import-path fix.

Original saved586 is retained in moved503file game tree593-kit/game. Newsave593
and result593 remain absent. Old result586 untouched. No PC runtime reopening.
Load and performance remain subsequent work; all deferred scopes unchanged.
