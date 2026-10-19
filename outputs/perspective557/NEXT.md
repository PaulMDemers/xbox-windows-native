# 557 prepared comparison workflow

Await actual answer to cold-start request. User asked to power off 10 seconds,
turn on and leave UnleashX. Do not infer readiness from FTP. Record exact answer,
UTC,user_confirmed_full_power_cycle=true,at_dashboard=true in ready001.json.
Then package.py, supervise.py stage, one supervise.py launch, observe.py.
Hook-FIRST supervise.py collect after dashboard return. audit.py 1 under WSL,
review_runtime.py,module_review.py,actual_controls.py,close.py. Preserve failure.
No package/stage/launch until readiness. Do not change frozen inputs afterward.
