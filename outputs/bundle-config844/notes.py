"""Copy plain-language limitations beside each private archive without changing ZIPs."""
import shutil
from pathlib import Path

root = Path('D:/xwn844')
shutil.copyfile(Path(__file__).with_name('COPYING.txt'), root / 'COPYING.txt')
notes = {
    'xbox16-720p-002': '1.6 fixed 720p: the historical 843 desktop and preconnected mouse worked, but shutdown stalled and needed a manual restart. This permanent-path rebuild has not yet been boot-tested.',
    'xbox10-720p-002': '1.0 720p: historically observed desktop and restart used selected matching components; the current bundle uses stock baseline hives with targeted matching registry keys. This newly assembled bundle has not yet been boot-tested.',
    'xbox10-480p-001': '1.0 720x480 progressive: drawing and input were observed in 638/642; a later selector boot failed. This newly assembled bundle has not yet been boot-tested.',
    'xbox10-1080i-002': '1.0 1080i: prior viewing showed text gaps and motion/window-drag artifacts; interlaced field and scanout quality remain unresolved. The stock E installer and this newly assembled bundle have not yet been boot-tested.'}
for name, note in notes.items():
    p = root / name / 'KNOWN-ISSUES.txt'
    with p.open('x', encoding='utf-8') as f:
        f.write(note + '\n')
print('Copied shared instructions and profile limitations')
