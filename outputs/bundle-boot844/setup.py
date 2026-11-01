from pathlib import Path
K=Path(__file__).resolve().parent; old=K.parent/'boot720-input843'
for n in ['main.c','Makefile','layout.c','layout.h','plan.c','plan.h','page.c','page.h','bridge.S','plan_test.py','retain835.c']:
 (K/n).write_bytes((old/n).read_bytes())
for source,target in [('build-chain002.py','chain.py'),('host007.py','host.py')]:
 t=(old/source).read_text().replace('boot720843-source001','bundle-boot844-source001').replace('/mnt/c/xwn843/chain002','/mnt/d/xwn-bundle844/chain001').replace('/mnt/c/xwn843/host007','/mnt/d/xwn-bundle844/host001').replace("'chain002.json'","'chain001.json'").replace("'host007.json'","'host001.json'")
 (K/target).write_text(t)
