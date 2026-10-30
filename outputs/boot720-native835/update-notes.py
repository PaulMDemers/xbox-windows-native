from pathlib import Path
W=Path(__file__).resolve().parents[2]
header=Path(__file__).with_name('NEXT.md').read_bytes()+b'\n\n'
for p in [W/'outputs/engineering-notes/CONTINUATION.md',W/'outputs/engineering-notes/STATUS.md',W/'docs/current-status.md']:
 old=p.read_bytes()
 if not old.startswith(header):p.write_bytes(header+old)
