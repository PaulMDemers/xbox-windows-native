"""Record accepted835 Windows launch. No hardware I/O."""
import json
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];r=json.loads((K/'launch001.json').read_text())
assert r['requested'] and r['reply']=='200 EXEC command succeeded.'
text='''# Fixed720p Windows boot835 launched once; screen observation pending

One SITE accepted at '''+r['utc']+'''. No retry. Windows boot intended.
This is the fixed720p path requested by the user, not another mode-setting probe.
Kernel establishes1280x720x32/pitch5120; loader retains timings/encoder, relocates
scanout to03700000 and preserves the9MiB retail64 Windows framebuffer reservation.
Existing Windows drivers unchanged. Normal startup leaves desktop running.

Installation complete:6563 payload files /703289963bytes, all read back, journal
reconciled. Three fresh boot executables and owner verified under XWN16Boot835.
Preparation/source evidence pushed82e6ec31. No startup hook, no console C access,
no owned host runtime. Automation remains paused; direct user work authorized.

Next obtain actual screen state after about2min. Offline FTP does not prove a
crash or Windows boot. Do not repeat835 or launch anything while it is offline.
Expected blue preparation, loader text, Windows desktop. Leave a working desktop
running; prefer normal Windows restart for later persistence/collection checks.
If stuck before Windows, preserve observation then request power off/on; after
authenticated dashboard return collect xwn-boot835 preparation once. The old JSON
tool label831 is inherited text; filename namespace, binary and owner identify835.

Capacity834 CLOSED PASS and831 CLOSED FAIL: never reopen. Mismatch832 stopped
source-only at user's direction. No encoder/timing campaign or new mode probe.
All host fixtures closed. Logic/CPU checks pass; physical Windows result unknown.
'''
(K/'NEXT.md').write_text(text)
for p in [W/'outputs/engineering-notes/CONTINUATION.md',W/'outputs/engineering-notes/STATUS.md',W/'docs/current-status.md']:
 p.write_bytes(text.encode()+b'\n'+p.read_bytes())
