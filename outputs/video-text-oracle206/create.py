"""New unique206 siblings with actual input-clip oracle; preserve failed204 unchanged."""
import hashlib,json,shutil
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];old=k.parent/'video-text-runtime204'
assert not (k/'gdi-probe.c').exists()
for name in ['gdi-probe.c','text-cases.c','common.py','Run.ps1','supervise-emulator.py','typed-state.py','audit-emulator.py','prepare-emulator.py',
             'runner_analysis.py','boundary_analysis.py','interval_policy.py','sample_analysis.py','dib_analysis.py','timing_analysis.py','window_analysis.py','text_analysis.py','review-build.py','Build-Probe.ps1','compare.py','test-parser.py']:
 s=(old/name).read_text(encoding='utf-8').replace('text204','text206').replace('text-runtime204','text-oracle206').replace('text-bounds203','text-clip205')
 if name=='gdi-probe.c':s=s.replace('"XWN_GDI_PROBE_VERSION",10,W,H','"XWN_GDI_PROBE_VERSION",11,W,H').replace('XwnGdiProbeV10','XwnGdiProbeV11')
 if name=='sample_analysis.py':s=s.replace("'10','256','128'","'11','256','128'")
 if name=='text-cases.c':
  s=s.replace('zero(d,128);return ExtEscape(Screen,0x58574436,0,NULL,128','zero(d,160);return ExtEscape(Screen,0x58574437,0,NULL,160')
  s=s.replace('before[32],after[32]','before[40],after[40]').replace('for(i=0;i<32;i++)record("TEXT_', 'for(i=0;i<40;i++)record("TEXT_')
  s=s.replace('before[1]!=117||after[1]!=117','before[1]!=118||after[1]!=118').replace('before[2]!=128||after[2]!=128','before[2]!=160||after[2]!=160')
  s=s.replace('after[30]||after[31]', 'after[30]||after[31]||after[38]||after[39]||after[37]>1')
  s=s.replace('    if(!textsnapshot(before))', '    record("TEXT_CLIENT_case_width_height",stage,(DWORD)client.right,(DWORD)client.bottom);\n    record("TEXT_ORIGIN_case_x_y",stage,(DWORD)origin.x,(DWORD)origin.y);\n    if(!textsnapshot(before))')
  s=s.replace('BOOL inside=textinside(stage,x,y);', 'BOOL inside=textinside(stage,x,y);\n            if(after[37])inside=inside&&x+origin.x>=(LONG)after[32]&&x+origin.x<(LONG)after[34]&&y+origin.y>=(LONG)after[33]&&y+origin.y<(LONG)after[35];')
 if name=='text_analysis.py':
  s=s.replace("10,256,128", "11,256,128").replace('13*64','13*80').replace('len(v)==32','len(v)==40').replace('list(range(32))','list(range(40))').replace('117,128,mode','118,160,mode')
  s=s.replace('a[30:]==[0,0]', 'a[30:32]==[0,0] and a[38:]==[0,0] and a[37] in [0,1] and a[36] in [0,1,3]')
  s=s.replace("actual=j(a,9)-j(b,9)", '''geo=[q for q in n if q[0]=='TEXT_CLIENT_case_width_height' and q[1]==case];origin=[q for q in n if q[0]=='TEXT_ORIGIN_case_x_y' and q[1]==case]
   assert len(geo)==len(origin)==1 and 256<=geo[0][2]<=1024 and 128<=geo[0][3]<=1024
   assert origin[0][2]<1024 and origin[0][3]<1024
   def signed(v):return v if v<0x80000000 else v-(1<<32)
   bound=list(map(signed,a[22:26]));clip=list(map(signed,a[32:36]));ox,oy=origin[0][2:]
   oracle=0
   if calls:
    for y in range(geo[0][3]):
     for x in range(geo[0][2]):
      inside=(case!=10 or 10<=x<133 and 12<=y<73) and (case!=11 or 5<=x<85 and 5<=y<70 or 140<=x<245 and 18<=y<117)
      if a[37]:inside=inside and clip[0]<=x+ox<clip[2] and clip[1]<=y+oy<clip[3]
      if mode:inside=inside and bound[0]<=x+ox<bound[2] and bound[1]<=y+oy<bound[3] and a[20]!=1
      if inside:oracle+=4
   actual=j(a,9)-j(b,9)''')
  s=s.replace("j(a,27)==actual==expected[0][2]", "j(a,27)==actual==expected[0][2]==oracle")
  s=s.replace("bounds=a[22:26] if calls else None", "bounds=a[22:26] if calls else None,input_clip=a[32:36] if calls else None,clip_complexity=a[36] if calls else None,client=geo[0][2:],origin=origin[0][2:]")
 if name=='review-build.py':
  s=s.replace("assert 'if(delta!=1&&!(stage==3&&delta==0))'", "assert 'if(after[37])inside=' in s\nassert 'if(delta!=1&&!(stage==3&&delta==0))'")
 if name=='compare.py':
  s=s.replace("assert table[0]['calls']==1 and table[0]['candidate_bytes']<table[0]['control_bytes']", "assert table[0]['calls']==1\nimprovement=any(v['candidate_bytes']<v['control_bytes'] for v in table)")
  s=s.replace('passed=True,physical_access=False,rows=table', 'passed=True,optimization_demonstrated=improvement,physical_testing_ready=improvement,physical_access=False,rows=table')
  s=s.replace('Exact text-copy reduction with same visible pixels', 'Actual input-clip matched text-copy comparison with same visible pixels')
 (k/name).write_text(s,encoding='utf-8',newline='\n')
(k/'artifacts').mkdir(exist_ok=False)
for name in ['runner.exe','wizard.exe']:shutil.copyfile(old/'artifacts'/name,k/'artifacts'/name)
print('New206 actual-input-clip probe/strict oracle prepared; no launch')
