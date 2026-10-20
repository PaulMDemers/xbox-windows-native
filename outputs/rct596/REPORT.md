# Xbox RCT596: manual save/load works

The user reports repeated manual saving and loading worked after the cold-start
launch. Cold collection retained a new Dynamite Dunes.SV4 (287269 bytes; see the
collection manifest for the measured size and SHA256), whileXWN586.SV4 and
XWN593.SV4 remained unchanged. The user rebooted the console, and a newEventLog6006
records normal Windows shutdown. Sound and performance were not tested.

The recorder reached a paused Forest Frontiers scene and collected13valid images.
It later saw a Load Game dialog; its manual interval and restoration code did not
finish before reboot. The screenshots do not contain the planned moved/restored
pair for exact593 reload. Treat the user's successful manual behavior as that
evidence class, not as an automated test pass. The separate595 attempt failed
during Windows loading and produced no runner results.

## Cleanup and retained limitations

The startup hook was removed first. All system/user hives were structurally
consistent and independent raw readers agreed. Ftdisk49 recurred. The runner's
three temporary game setup values remained; original registry review failed.
A reviewed offline cleanup removed exactly those two keys and three values,
preserving all other postrun key names/rawvalues and all game saves. Eight modeled
transaction cases passed. The installed candidate and retained rollback were
read back twice using fresh FTP sessions. The original postrunSOFTWARE remains
at/E/xwn586-kit/software-before596.hiv. Registry-review002 confirms restoration.
No Windows boot was performed after that cleanup.

Initial cleanup preparation rejected incomplete typed decoding of an existing
DRMDataPath type1004. That failure and candidate are retained. Corrected preparation
requires the exact same typed error and raw value before/after, plus agreement of
two independent raw hive readers. This limitation is explicit, not a claim of
complete typed decoding. Full FATX allocation, prolonged play, fullscreen,
frame rate and native GPU acceleration remain unqualified.

See final001.json, user-observation001.json, collection001.json, audit1.json,
visual-review001.json, cleanup-preparation002.json, cleanup-host001.json,
cleanup-apply001.json and registry-review002.json. All host processes closed;
console last at dashboard, ordinary launcher720p preserved, no startup hook.
