"""New fixed-arithmetic characterization; never changes failed 484 inputs."""
from pathlib import Path
import re
K=Path(__file__).resolve().parent;W=K.parents[1];old=K.parent/'d3d-blend484'
s=(W/'src/samples/graphics-ladder/blend.c').read_text()
a=s.index('static VERTEX vertices[]');b=s.index('static HANDLE log_file',a)
stages=['clear','zeroone','onezero','a0','a85','a170','a255','disabled']
alphas=[85,85,0,85,170,255,85]
vertices=',\n '.join('{%s,%s,.5f,1,0x%02xc97539}'%(x,y,alpha) for alpha in alphas for x,y in [(8,8),(56,8),(8,56)])
s=s[:a]+'static VERTEX vertices[]={\n '+vertices+'};\n'+\
 'static const char *const stages[]={'+','.join('"'+x+'"' for x in stages)+'};\n'+\
 'static const char *const suffixes[]={'+','.join('"-'+x+'.bin"' for x in stages)+'};\n'+\
 'static const DWORD alphas[]={0,85,85,0,85,170,255,85};\n'+\
 'static const DWORD sources[]={5,1,2,5,5,5,5,5},destinations[]={6,2,1,6,6,6,6,6};\n'+\
 'static HANDLE captures[8];\n'+s[b:]
s=s.replace('i<6','i<8').replace('i==5','i==7').replace('0x0000ff00','0x002468ac')
s=s.replace('DWORD enabled=i==7?FALSE:TRUE;','DWORD enabled=i==7?FALSE:TRUE;\n  wsprintfA(key,"%s.set_src",stages[i]);RS(key,D3DRENDERSTATE_SRCBLEND,sources[i]);\n  wsprintfA(key,"%s.set_dest",stages[i]);RS(key,D3DRENDERSTATE_DESTBLEND,destinations[i]);')
s=s.replace('value!=D3DBLEND_SRCALPHA','value!=sources[i]').replace('value!=D3DBLEND_INVSRCALPHA','value!=destinations[i]')
s=s.replace('xwn-d3d-blend-1','xwn-d3d-precision-1').replace('XWND3DBlend08c','XWND3DPrecision486')
p=K/'precision.c';assert not p.exists();p.write_text(s,encoding='utf-8',newline='\n')
s=(W/'tools/graphics_blend.py').read_text()
s=s.replace('BG, FG = 0x102030, 0x40c080\n','').replace("STAGES = ('clear', 'a0', 'a85', 'a170', 'a255', 'disabled')",'STAGES = '+repr(tuple(stages)))
s=s.replace('ALPHAS = (0, 0, 85, 170, 255, 85)','ALPHAS = (0,85,85,0,85,170,255,85)\nSOURCES = (5,1,2,5,5,5,5,5)\nDESTINATIONS = (6,2,1,6,6,6,6,6)').replace('BG, FG = 0x00ff00, 0xff00ff','BG, FG = 0x2468ac, 0xc97539')
s=s.replace("('set_blend','get_blend'","('set_src','set_dest','set_blend','get_blend'")
a=s.index('def allowed(');b=s.index('\ndef validate(',a)
s=s[:a]+'''MODELS=('ideal_nearest255','combined_floor256','separate_floor256')
def expected(stage,model):
    if stage in ('clear','zeroone'):return BG
    if stage in ('onezero','disabled'):return FG
    alpha=ALPHAS[STAGES.index(stage)];rgb=0
    for shift in (16,8,0):
        source=(FG>>shift)&255;dest=(BG>>shift)&255
        if model=='ideal_nearest255':v=(source*alpha+dest*(255-alpha)+127)//255
        elif model=='combined_floor256':v=(source*alpha+dest*(255-alpha))//256
        elif model=='separate_floor256':v=source*alpha//256+dest*(255-alpha)//256
        else:raise ValueError('Unknown arithmetic model')
        rgb|=v<<shift
    return rgb
def pixels(*frames):
    if len(frames)!=8 or any(len(f)!=16384 for f in frames):raise ValueError('Capture length/count')
    matching=[]
    for model in MODELS:
        valid=True
        for stage,frame in zip(STAGES,frames):
            want=expected(stage,model)
            for index,(word,) in enumerate(struct.iter_unpack('<I',frame)):
                x,y=index%64,index//64;rgb=word&0xffffff
                if x>=12 and y>=12 and x+y<=56:allowed={want}
                elif x<=4 or y<=4 or x+y>=72 or x>=60 or y>=60:allowed={BG}
                else:allowed={BG,want}
                if rgb not in allowed:valid=False;break
            if not valid:break
        if valid:matching.append(model)
    if len(matching)!=1:raise ValueError('No unique predefined arithmetic model: '+repr(matching))
    return dict(characterization_only=True,matching_model=matching[0],original_484_requalified=False,strict_ideal_model=matching[0]=='ideal_nearest255')
'''+s[b:]
s=s.replace('xwn-d3d-blend-1','xwn-d3d-precision-1').replace("'0' if i==5 else '1'","'0' if i==7 else '1'").replace("stage+'.src':'5',stage+'.dest':'6'","stage+'.src':str(SOURCES[i]),stage+'.dest':str(DESTINATIONS[i])")
s=s.replace('for a in (0,85,170,255,85)','for a in (85,85,0,85,170,255,85)').replace("unhex(f['vertices'],300,300)","unhex(f['vertices'],420,420)")
s=s.replace("scope='RGB software SRCALPHA/INVSRCALPHA diffuse blending; partial RGB allows one level rounding; exact edges, destination alpha, presentation and speed unqualified'","scope='Fixed mixed-color arithmetic characterization; not exact alpha qualification or an implementation trace'")
p=K/'graphics_precision.py';assert not p.exists();p.write_text(s,encoding='utf-8',newline='\n')
for name in ['runner.c','binary-review001.py','prepare001.py','cold002.py','preflight001.py','run001.py','login001.py','review001.py','independent001.py','module-review001.py','closeout001.py']:
    s=(old/name).read_text();s=re.sub(r'(?<![0-9])484(?![0-9])','486',s).replace('d3d-blend486','blend-precision486').replace('graphics_blend','graphics_precision').replace('r08cd','p486d').replace('r08cs','p486s')
    s=s.replace("W/'tools/graphics_precision.py'","K/'graphics_precision.py'").replace("W/'src/samples/graphics-ladder/blend.c'","K/'precision.c'").replace("W/'src/samples/graphics-ladder/blend.cmd'","K/'DESIGN.md'").replace("W/'tests/test_graphics_precision.py'","K/'oracle-tests001.py'")
    s=s.replace('scoped_blend_passed','arithmetic_characterization_passed')
    if name=='review001.py':s=s.replace("'offscreen diffuse alpha controls'","'offscreen arithmetic characterization'")
    if name=='closeout001.py':s=s.replace("n=read(K/'actual-controls001.json')","n=read(K/'actual-controls001.json')")
    p=K/name;assert not p.exists();p.write_text(s,encoding='utf-8',newline='\n')
for name in ['launch_gate.py','floppy_check.py','floppy-tests001.py','inherited-gate-tests001.json']:
    p=K/name;assert not p.exists();p.write_bytes((old/name).read_bytes())
print('New 486 fixed-model sample/decoder and controller sources only.')
