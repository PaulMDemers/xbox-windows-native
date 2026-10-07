"""Create a separate diagnostic kit only after the ordinary pair passes."""
from pathlib import Path
import json,shutil
p=Path(__file__).resolve().parent;k=p.parent/'video-ram-scanout'
assert json.loads((p/'pair-review.json').read_text())['passed'];k.mkdir(exist_ok=False)
for name in ['display','tests']:shutil.copytree(p/name,k/name)
for name in ['0108-ram-primary.patch','patch-review.json','build-report.json','source-verification.json','host-tests.json','tests-body.c']:
 shutil.copyfile(p/name,k/name)
(k/'candidate001/artifacts').mkdir(parents=True);shutil.copyfile(p/'candidate001/artifacts/xwnram.dll',k/'candidate001/artifacts/xwnram.dll');shutil.copyfile(p/'candidate001/build.json',k/'candidate001/build.json')
(k/'artifacts').mkdir()
for name in ['atomic_json.py','audit.py','configuration.py','cold-map.py','preflight.py','Run.ps1','supervise.py','record-closure.py','common.py','prepare.py','review.py','Build-Probe.ps1','probe.c']:
 s=(p/name).read_text().replace('video-ram-primary','video-ram-scanout').replace('nt5-vram-','nt5-vrscan-').replace('xwnram114','xwnscan115')
 if name in ['common.py','probe.c']:s=s.replace('114','115')
 if name=='preflight.py':s=s.replace('debugger=False','debugger=True')
 if name=='audit.py':s=s.replace('debugger=False','debugger=True');s += "\nr=read(out/'audit.json');r['ordinary_qualified']=False;r['limits']='Debugger diagnostic only; independent physical-buffer verification is separate.';save(out/'audit.json',r)\n"
 if name=='supervise.py':
  s=s.replace('for cycle in [1]:',"assert (k/'trace-armed.signal').exists(), 'Observer must be armed before launch'\nfor cycle in [1]:")
 if name=='common.py':
  s=s.replace("        for size,", "        take('CURSOR_PARKED',[1000,550,0])\n        for size,")
 if name=='probe.c':
  a=s.index('__declspec(dllexport)');b=s.index('\n\ntypedef',a)
  s=s[:a]+'''__declspec(dllexport) __attribute__((noinline,noclone,used,externally_visible)) DWORD __cdecl XwnScanout(DWORD phase,DWORD size,DWORD kind,LONG x,LONG y){__asm__ volatile("":::"memory");return phase^size^kind^(DWORD)x^(DWORD)y;}
static DWORD XwnPhase(DWORD phase,DWORD size,DWORD kind,HDC screen,HDC memory,HWND window){POINT p={0,0};(void)screen;(void)memory;if(!ClientToScreen(window,&p))ExitProcess(30);return XwnScanout(phase,size,kind,p.x,p.y);}
'''+s[b:]
  s=s.replace(' for(s=0;s<3&&!Failures;s++){',' if(!SetCursorPos(1000,550)||!GdiFlush()){ExitProcess(31);}\n record("CURSOR_PARKED",1000,550,0);\n for(s=0;s<3&&!Failures;s++){')
 (k/name).write_text(s,newline='\n')
