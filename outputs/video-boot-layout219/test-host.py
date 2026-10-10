"""Actual source-body guard tests with ASan/UBSan, not runtime qualification."""
import hashlib,json,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];attempt=sys.argv[1]
assert attempt=='002';out=k/('artifacts/host'+attempt);dest=k/('host-tests'+attempt+'.json')
assert not out.exists() and not dest.exists();out.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
review=json.loads((k/'source-review.json').read_text());assert review['passed']
candidate=k/'artifacts/source/drivers/base/bootvid/i386/xbox/bootvid.c';assert sha(candidate)==review['candidate_bootvid_sha256']
parent=ws/'outputs/video-gpu-transfer-contract212/artifacts/boot-reservation/drivers/base/bootvid/i386/xbox/bootvid.c'
names=['ApplyPalette','ResetDisplay','InitPaletteWithTable','SetPixel','PreserveRow','DoScroll','DisplayCharacter','VidSolidColorFill','VidScreenToBufferBlt']
def body(text,name):
    import re
    match=re.search(r'(?m)^(?:static )?(?:VOID|UCHAR)\n(?:NTAPI\n)?'+name+r'\(',text);assert match,name
    start=match.start();brace=text.index('{',match.end());depth=1;i=brace+1
    while depth:
        if text[i]=='{':depth+=1
        elif text[i]=='}':depth-=1
        i+=1
    return text[start:i]
r=dict(passed=False,source_sha256=sha(Path(__file__)),harness_sha256=sha(k/'test-drawing.c'),layout_sha256=sha(k/'boot_layout.h'),source_bodies={},runs=[])
for label,source,control in [('control',parent,1),('candidate',candidate,0)]:
    d=out/label;d.mkdir();inc=d/'actual-drawing.inc';inc.write_text('\n\n'.join(body(source.read_text(),n) for n in names)+'\n')
    r['source_bodies'][label]=dict(full_source_sha256=sha(source),extracted_sha256=sha(inc),names=names)
    binary=d/'drawing';command=['/usr/bin/gcc','-std=c11','-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer','-DCONTROL='+str(control),'-I'+str(d),'-I'+str(k),str(k/'test-drawing.c'),'-o',str(binary)]
    subprocess.run(command,check=True);got=subprocess.check_output([str(binary)],text=True);row=json.loads(got);assert row['passed']
    r['runs'].append(dict(label=label,result=row,command=command,binary_sha256=sha(binary)))
r['passed']=True;r['limits']='Actual extracted drawing/reset bodies with modeled host HAL/palette/font; not actual kernel initialization, timing, interrupts, cache or GPU ownership.'
r['compiler_sha256']=sha(Path('/usr/bin/gcc').resolve())
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps([v['result'] for v in r['runs']]))
