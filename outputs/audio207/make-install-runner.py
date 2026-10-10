import pathlib
k=pathlib.Path(__file__).resolve().parent;p=k/'install-runner.c';assert not p.exists()
s=(k/'runner.c').read_text().replace('runner207.log','install-runner207.log').replace('RUNNER207','INSTALL_RUNNER207').replace('probe.exe','install.exe').replace('PROBE','INSTALLER')
p.write_text(s)
