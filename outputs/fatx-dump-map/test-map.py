"""Compile actual mapping functions with host mocks and ASan/UBSan."""
import hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;src=Path('/home/paul/xbox-windows-native/build/fatx-directory-order-001/source/drivers/filesystems/vfatfs/rw.c')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
text=src.read_text();part=text[text.index('NTSTATUS\nVfatBuildPagingMap('):text.index('static NTSTATUS\nVfatPagingFileIo(')]
(k/'artifacts/paging-builder.inc').write_text(part)
compiler='/usr/bin/gcc';exe=k/'artifacts/test-map';args=[compiler,'-std=gnu11','-Wall','-Wextra','-Werror','-Wno-multichar','-fsanitize=address,undefined','-fno-omit-frame-pointer','-g',str(k/'test-map.c'),'-o',str(exe)]
subprocess.run(args,check=True);result=subprocess.check_output([str(exe)],text=True)
report=dict(scope=__doc__,compiler=compiler,compiler_version=subprocess.check_output([compiler,'--version'],text=True).splitlines()[0],command=args,source_sha256={n:sha(k/n) for n in ['test-map.c','dump-map.inc','artifacts/paging-builder.inc']},builder_source_sha256=sha(src),output=result,passed=True,limits='Host layout/mocks, not NT ABI, actual SEH exceptions, guest lifecycle or dump-write qualification.')
path=k/'map-tests.json';assert not path.exists();path.write_text(json.dumps(report,indent=2)+'\n');print(result)
