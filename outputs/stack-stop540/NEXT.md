#540 staged; await watcher/reset readiness before launch

Read REPORT.md, DESIGN.md, package001.json and supervisor-stage.json. The stage
supervisor is closed/completed, no launch or hook exists. Do not modify frozen
code/package pins or restage. Candidate deliberately stops before Windows.

Pending question: user can watch the front LED and manually reset afterward.
When explicitly confirmed, save ready1.json (ordinal1,ready=true,watching_LED=true,
manual_reset_available=true, exact user observation, UTC). It is observation
availability, not another permission request. If unavailable, leave staged.

Run frozen supervise.py before1 once using active session FTP configuration. Verify
all ten files equal retained539 after1; controller also checks them immediately
before dispatch. Then launch1 once;20-second SITE reply bound, no retries after
accepted/uncertain launch. Existing hardware lease and20GiB+64MiB guard apply.

Announce launch and request the front-LED sequence over about30seconds: amber,
alternating red/green, any other state, plus screen/dashboard behavior. A positive
red/green supports reaching the checkpoint, not HLT or complete marker success.
It is intended to stop; do not wait for Windows or automatic dashboard return.
After the observation, request power off/on to UnleashX. Record the exact report
and manual reset separately. If it returns by itself, preserve that instead.

Once user confirms dashboard, save observer1.json with user_report_received and
at_dashboard true and exact reset/LED facts. No temporary hook to remove. Run
supervise.py after1 once, WSL audit.py1 and Windows decode_actual.py1. Receipts
still describe pre-handoff state only. Event-log equality and registry cleanliness
are not normal Windows shutdown proof; no Windows workload is intended.

Close with source/binary pins, exact observations, cold audits and supervisor state;
review/check/commit/push. No second launch, control fallback or reuse/recollection
of closed539/536. A fresh test is not proof of what happened in those attempts.
Keep all physical/host/model evidence separate. Preserve720p, ordinary launcher,
startup, recovery, and console C exclusion. No D3D/GPU/game/release promotion.
