import sys,runpy
from pathlib import Path
sys.argv += ['--corrupt','system-pte']
runpy.run_path(str(Path(__file__).with_name('trace-early.py')),run_name='__main__')
