"""Keep rejected host005/cpu009 receipts; bind fresh checks to chain002."""
from pathlib import Path
K=Path(__file__).resolve().parent
p=K/'host006.py';assert not p.exists()
p.write_text((K/'host005.py').read_text().replace('host005','host006').replace('chain001','chain002'))
p=K/'cpu005.py';assert not p.exists()
p.write_text((K/'cpu004.py').read_text().replace('host005','host006').replace('cpu004','cpu005').replace('cpu-build009','cpu-build010').replace('cpu-run009','cpu-run010'))
p=K/'build001.py';p.write_text(p.read_text().replace('host005','host006').replace('chain001','chain002').replace('cpu-run009','cpu-run010'))
