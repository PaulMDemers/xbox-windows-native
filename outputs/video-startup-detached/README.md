# Detached startup protocol experiment

The candidate0096 driver,120-second runner, GDI probe, clean source fixture and
strict cold checks are unchanged. Only the startup command changes from a
synchronous runner invocation to `start "" C:\xwnlag01\runner.exe`, then exits.
This lets the startup CMD finish before the runner asks Windows to restart.

One ordinary debugger-free run passed: all four GDI copy checks, five bounded
timing records, actual direct-RAM UC mapping, payload hashes, normal shutdown and
one dashboard return. No new application events or shutdown popups were logged.
See audit.json and launch.json. This supports a test-launcher timing hypothesis;
one clean run does not establish causality or erase the two synchronous failures.
The120-second delay alone previously failed. No popup waiver was added.

A subsequent run with the new0097 ReactOS display replacement and this detached
launcher again logged two shutdown popups. Thus detaching startup is not a
demonstrated general fix. See ../video-surface-lifecycle for that separate build.

No physical deployment occurred. This experiment is not a hardware speedup,
full PnP lifetime qualification or release promotion. The physical0093 baseline
and Microsoft display DLL remain unchanged.
