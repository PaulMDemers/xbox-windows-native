"""Create a fresh repeat-test kit; failed336 disk is never a parent."""
from pathlib import Path
import json
K=Path(__file__).resolve().parent;old=K.parent/'stock-repeat336';new=K.parent/'stock-repeat339';assert not new.exists();new.mkdir()
t=(K.parent/'hd-ui313/test-analysis.py').read_text().replace("('GUI_ACTIVATE_BEFORE313_ACTIVE',[0,20,21])", "('GUI_ACTIVATE_BEFORE313_ACTIVE',[0,0,0])")
t=t.replace('(15,0,4999)', '(15,0,4999),(5,1,20),(5,1,99),(10,1,0)')
(K/'test-analysis.py').write_text(t,newline='\n')
for n in ['analyze-allocation002.py','analyze-capture.py','installed-binding.py','typed-state.py','stock_io002.py','Invoke.ps1','.gitignore']:(new/n).write_bytes((old/n).read_bytes())
for n in ['Prepare.ps1','Run.ps1','close-host.py','supervise.py','verify-repeat.py']:
    t=(old/n).read_text().replace('stock-repeat336','stock-repeat339').replace('xwn336','xwn339').replace('stock336','stock339').replace('5123','5126').replace('5124','5127').replace('5125','5128')
    (new/n).write_text(t,newline='\n')
t=(old/'audit002.py').read_text().replace('xwn336','xwn339').replace('stock336','stock339');(new/'audit.py').write_text(t,newline='\n')
t=(old/'prepare.py').read_text().replace('xwn336','xwn339').replace('stock336','stock339')
t=t.replace("data=w.read('xwndemo251/'+name);r['changes'].append(w.write('xwnstock339/'+name,data))", "data=w.read('xwndemo251/'+name)\n            if name=='wizard.exe':\n                data=Path('/mnt/e/xwn338/build001/wizard.exe').read_bytes();assert m.sha(data)==json.loads((K.parent/'stock-focus338/build-review001.json').read_text())['binary_sha256']\n            r['changes'].append(w.write('xwnstock339/'+name,data))")
t=t.replace("r.update(prepared=True,source_sha256=f['fixture_sha256']", "f['protected']={**f['protected'],**{'E/'+v['path']:v['sha256'] for v in r['changes']}}\n    r.update(prepared=True,source_sha256=f['fixture_sha256']")
(new/'prepare.py').write_text(t,newline='\n')
t=(old/'freeze.py').read_text().replace("pins[str(p.relative_to(W))]", "pins[p.relative_to(W).as_posix()]")
t=t.replace("pins={}", "paths+=list((K.parent/'stock-focus338').glob('*.py'))+list((K.parent/'stock-focus338').glob('*.h'))+list((K.parent/'stock-focus338').glob('*.inc'))+list((K.parent/'stock-focus338').glob('*.c'))+[K.parent/'stock-focus338/build-review001.json']\npins={}")
(new/'freeze.py').write_text(t,newline='\n')
(new/'DESIGN.md').write_text('Fresh repeat boot from successful335 persisted hives/trace, not failed336. Same stock10GB/E-only layout and saved first-boot artifacts; fresh xwnstock339 helper namespace. Only338 emulator activation helper differs from336. Five drawing samples, six audio phases, normal restart and full cold audit remain required. Require independent actual inactive-target activation evidence in addition to original setup/Cancel/workload gates. Preserve missing activation coverage as a distinct failure. No physical deployment.\n')
