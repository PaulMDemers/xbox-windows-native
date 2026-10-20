"""Require additional post-run timing and address reviews before immutable closure."""
from pathlib import Path
import json,runpy
K=Path(__file__).resolve().parent
for n in ['location-review001.json','syscall-review001.json','timing-bound-review001.json']:
 assert json.loads((K/n).read_text())['passed'],n
runpy.run_path(str(K/'close002.py'),run_name='__main__')
