"""Explicit native-library environment for retained cold002 auditor."""
import os,subprocess,sys
from pathlib import Path
env=os.environ.copy();env['LD_LIBRARY_PATH']='/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/x86_64-linux-gnu'
p=subprocess.run([sys.executable,'-B',str(Path(__file__).with_name('cold002.py')),*sys.argv[1:]],env=env,timeout=240)
sys.exit(p.returncode)
