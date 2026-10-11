"""Bind separately inspected native-window images to journaled emulated input."""
import datetime,hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;case=k/'veto001';art=case/'artifacts/runtime'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sys.path.insert(0,'C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/work/python-packages')
from PIL import Image
t=read(case/'trace.json');run=read(case/'run.json');lease=read(case/'ui-lease001.json');close=read(case/'ui-lease001-closed.json');close2=read(case/'ui-lease002-closed.json')
when=lambda x:datetime.datetime.fromisoformat(x.replace('Z','+00:00'))
rows=[]
for name,command,image,observation in [
 ('input003-keyboard.json','sendkey ctrl-esc','input003-keyboard.png','Guest Start menu visibly opened after both sharing failures.'),
 ('input003-restore.json','sendkey esc','input003-restore.png','Start menu closed; Found New Hardware Wizard and Getting Started windows remained.'),
 ('input004-mouse.json','mouse_move 80 60','input004-mouse.png','Guest arrow visibly moved from approximately window (642,518) to (843,662); no click was sent.')]:
    r=read(case/name);assert r['command']==command and r['pid']==run['pid']==lease['guest_pid']
    assert when(t['finished_utc'])<when(r['utc'])<when(run['closed_utc'])
    if '003' in name:assert when(lease['acquired_utc'])<when(r['utc'])<when(close['closed_utc'])
    else:assert when(r['utc'])<when(close2['closed_utc'])
    p=art/image;assert Image.open(p).size==(1282,992)
    rows.append(dict(command_journal=name,command=r['command'],utc=r['utc'],image=str(p),sha256=sha(p),visual_assessment=observation))
assert run['closed'] and t['breakpoints_remaining']==0
result=dict(review_passed=True,basic_emulated_keyboard_response_observed=True,basic_emulated_mouse_response_observed=True,full_input_qualified=False,physical_access=False,ordinary_boot_qualified=False,window_id=lease['window'],guest_pid=run['pid'],capture_method='Computer Use sky.get_window_state on uniquely selected xemu window; host Get-Process MainWindowHandle matched owned PID',baseline_image=str(art/'input003-before.png'),baseline_sha256=sha(art/'input003-before.png'),observations=rows,visual_assessment_method='Assistant inspected each displayed native-window screenshot; hashes and command ordering checked by this script. This is not an automated pixel oracle.',preserved_capture_failures=['input-check.py before: HMP screendump did not create the PPM; no input sent and response was not retained by that script.','input-check002.py before: linear guest-memory interpretation unreadable; no input sent. Do not infer a guest display failure from this image.','input003 mouse command: lease-expiry assertion prevented sending; input003-mouse.png is an unused unchanged-pointer snapshot. A new lease was acquired for the sole actual mouse_move recorded in input004-mouse.json.'],script_sha256=sha(Path(__file__)),limits='One Ctrl+Esc/Escape pair and one relative mouse movement after debugger cleanup. No text-entry, clicks, long-duration input, power-button/wake, normal restart, repeated boot or physical-console qualification. No setup dialog dismissed.')
dest=k/'input-review001.json';assert not dest.exists();dest.write_text(json.dumps(result,indent=2)+'\n');print('Post-failure basic keyboard and mouse observations bound to command/image evidence')
