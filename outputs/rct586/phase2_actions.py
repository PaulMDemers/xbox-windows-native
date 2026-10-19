"""MIT. Fixed owned phase2 actions: avoid host-shell loss of backslashes."""
import runpy,sys
from pathlib import Path
actions={
 'launch':['type','--text',r'C:\xwn586-kit\load586.exe'],
 'loadpath':['type','--text',r'C:\xwn586-kit\game\Saved Games\XWN586.SV4'],
}
key=sys.argv[1];assert key in actions
sys.argv=['vm_phase2.py','586']+actions[key]
runpy.run_path(str(Path(__file__).with_name('vm_phase2.py')),run_name='__main__')
