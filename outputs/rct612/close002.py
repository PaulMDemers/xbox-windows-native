"""Require the additional retry/lifetime checks before the retained closure."""
import json,runpy
from pathlib import Path
K=Path(__file__).resolve().parent
for n in ['retry-inheritance001.json','lifetime-inheritance001.json','space-review001.json','game-lifetime-tests001.json']:
 assert json.loads((K/n).read_text())['passed'],n
runpy.run_path(str(K/'close001.py'),run_name='__main__')
