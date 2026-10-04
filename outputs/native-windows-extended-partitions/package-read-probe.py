"""Package the opt-in read diagnostic and correct the generic packager's scope."""
import pathlib,subprocess,sys,json
kit=pathlib.Path(__file__).resolve().parent
dst=kit/'artifacts/extended-read.iso'
subprocess.run([sys.executable,str(kit.parent/'native-windows-nt5-kernel/make-iso.py'),'--output',str(dst),'--autorun','--loader-directory',str(kit/'artifacts'),'--hal-directory',str(kit/'artifacts')],check=True)
p=dst.with_suffix('.json');r=json.loads(p.read_text())
r.update(kernel_entry_enabled=False,scope='Opt-in extended F read preflight halts before Windows; HAL is packaged but not executed.')
p.write_text(json.dumps(r,indent=2)+'\n')
(kit/'iso-manifest.json').write_text(json.dumps(r,indent=2)+'\n')
