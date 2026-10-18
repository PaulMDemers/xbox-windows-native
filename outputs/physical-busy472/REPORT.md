# Physical busy correction472 — desktop observed, cold collection pending

The user reports: "It's at the desktop." One new corrected471 diagnostic was staged and read back in E:/Applications/XWNBoot471a. The dashboard accepted its only SITE EXEC request at2026-10-18 01:58:28UTC. This is one user-observed successful Windows boot; LED behavior was not reported. No launch retry is permitted.

The original E:/Applications/XWNEBoot/default.xbe, normal startup and720p configuration were verified before launch and not changed. No console C access. The preceding469 refusal at0x0808 is preserved.471 corrects host-busy handling in both marker locations and passed host/emulator gates. This does not establish a fix for the historical intermittent boot failure.

The90-second observer finished with dashboard FTP unavailable. After the user's desktop confirmation, a normal Windows Start/Shut Down/Restart was requested. The controller has not yet retrieved this run's report/refusal or cold files; the separate read-only return check also found FTP unavailable. Do not claim machine-captured physical marker completion, normal shutdown, durability, repeat-boot stability or D3D success yet.

Private before capture: C:/xwn472/physical001. See stage001.json, launch001.json, observation001.json, user-desktop001.json and return-check001.json. All owned launch/observer processes are closed. Collect once after actual dashboard return, then run cold-review001.py and closeout001.py; preserve partial/failure evidence. The owned new folder is diagnostic-only and is not the normal launcher.
