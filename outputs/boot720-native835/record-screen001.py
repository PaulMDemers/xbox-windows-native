"""Preserve the user's loader-error evidence privately; no console access."""
import datetime, hashlib, json
from pathlib import Path
K = Path(__file__).resolve().parent
W = K.parents[1]
source = Path('C:/Users/Paul/.codex/codex-remote-attachments/01a0ff98-aa67-78c0-baa4-279c9bacf1d2/09681521-0129-45B7-9DA4-4246CD19EBF9/1-Photo-1.jpg')
dest = Path('C:/xwn835/screen001.jpg')
assert not dest.exists() and not (K/'screen001.json').exists()
data = source.read_bytes()
dest.write_bytes(data)
r = {'utc_recorded': datetime.datetime.now(datetime.timezone.utc).isoformat(),
     'attempt': '835physical001', 'photo_bytes': len(data),
     'photo_sha256': hashlib.sha256(data).hexdigest(), 'private_photo': str(dest),
     'dialog': 'Could not load SYSTEM.ALT hive!',
     'observation': 'Readable FreeLoader dialog over repetitive green glyph background.',
     'windows_desktop_observed': False, 'nt_kernel_entry_proved': False,
     'primary_hive_failure_reason': 'Unknown: alternate error follows primary open/read/import failure.',
     'console_state': 'Last observed held loader error; power off/on requested, dashboard confirmation pending.',
     'hook': 'none installed', 'host_runtime': 'none owned'}
(K/'screen001.json').write_text(json.dumps(r, indent=2)+'\n')
note = '''# Boot835: FreeLoader SYSTEM.ALT error; awaiting dashboard return

Photo screen001.json shows "Could not load SYSTEM.ALT hive!" with a readable
dialog over repetitive green glyphs. The fixed720p path reached Windows hive
loading, but NT kernel entry and desktop are not proved. Primary SYSTEM failure
is unresolved; alternate failure does not establish a missing/corrupt primary.

One launch only, accepted 2026-10-30T11:45:56.944843+00:00. No retry. User was
asked to power off/on and leave UnleashX; confirmation remains pending. Do not
launch until dashboard is independently authenticated. No hook was installed.
After return, authenticate owner, collect835 preparation once, then audit the
installed SYSTEM against package/stage hashes before any repair. Preserve failed
attempt and photo privately. No owned host runtime. Automation remains paused.

Continue fixed720p Windows boot diagnosis only. Mode-setting campaign remains
stopped. Existing Windows drivers unchanged; installation6563 files read back.
Source-only investigation: actual loader includes separate hive initialize/check
dialogs. Inspect primary file open/read and boot path; do not blindly add ALT.
Boot835 remains OPEN pending collection; never relaunch this attempt.

'''
(K/'NEXT.md').write_text(note)
for p in [W/'outputs/engineering-notes/CONTINUATION.md', W/'outputs/engineering-notes/STATUS.md', W/'docs/current-status.md']:
    p.write_bytes(note.encode('ascii')+p.read_bytes())
print(json.dumps(r, indent=2))
