"""Read-only allocation capture for the closed owned soak rehearsal."""
import sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(k.parent/'fatx-mapped-eof'))
from allocation import scan
run=ws/'work/runs/nt5-fatx0098-soak-rehearsal'
assert (run/'cleanup.json').exists()
scan(run/'hdd.qcow2',k/'rehearsal/allocation-artifacts/artifacts')
