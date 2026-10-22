#647 staged; await LED/screen readiness, then at most one launch

Read REPORT.md,review001/build002 failures,build003.json,compiled-host001.json,
review003.json,host001.json and actual preparation001/stage001. No SITE yet.
Exact built/staged SHA9c62cd343a6236363716a395e740f890de83b8a05d0bf5c8be9b1ca3f0b899b4.
Original720p/startup remain exact. No hook or owned process. No existing runtime
is being reused; source came from the retained build tree, not a closed VM.

User was asked whether ready to watch the eight-second LED indication and screen.
After an explicit readiness reply, create ready001.json with watching_LED_and_screen
true and the actual response. Recheck review003 pass, staged bytes and source pins.
Use physical.py launch once (20s reply bound); never repeat accepted/uncertain.
Start observe.py once, bounded600s, no hook. Ask for the full LED sequence, last
screen and automatic dashboard return. If Windows opens, request normal Restart
after the observation. Do not assume indicator absence locates the failure.

If offline at deadline, record state and ask hardware observation/recovery rather
than another launch. On dashboard return collector captures fresh files once;
normal720p requires no restore because it was never replaced. Run audit.py on
retained files with the known private hivex library loader path, record observation
separately, then close and commit. No additional automatic launch is authorized
by a positive or negative result. A result narrows this instrumented run only.

Preserve build001 review rejection,build002 path failure and all prior failures.
Do not edit frozen controller/build sources after staging. No live switching,
boot reliability,other-revision or acceleration promotion. Automation remains paused.
