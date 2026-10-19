"""Independent cold image/control review for Save dialog inspection only."""
import hashlib,json,re,struct
from pathlib import Path
from PIL import Image
K=Path(__file__).resolve().parent;P=Path('C:/xwn578/pc001/collection001')
read=lambda n:json.loads((K/n).read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'dialog-review001.json';assert not out.exists()
col=read('collection001.json');assert col['completed'] and read('review001.json')['passed']
runner=(P/'runner.txt').read_text();assert sha(P/'runner.txt')==col['files']['xwn578/runner.txt']['sha256']
captures={};images={}
for name,row in col['files'].items():
 if not name.endswith('.bmp'):continue
 p=P/Path(name).name;b=p.read_bytes();assert sha(p)==row['sha256'] and len(b)==row['bytes']==1228854
 assert struct.unpack_from('<2sIHHI',b)==(b'BM',len(b),0,0,54)
 assert struct.unpack_from('<IiiHHII',b,14)==(40,640,-480,1,32,0,1228800)
 im=Image.open(p).convert('RGB');assert im.size==(640,480) and len(set(im.get_flattened_data()))>1
 images[p.stem[3:]]=im;captures[p.name]=dict(sha256=row['sha256'],bytes=len(b),nonuniform=True)
assert len(captures)==7
a=images['park-before-save'].crop((5,40,635,430));b=images['park-after-cancel'].crop((5,40,635,430))
changed=sum(x!=y for x,y in zip(a.get_flattened_data(),b.get_flattened_data()))
controls=[dict(hwnd=int(h),id=int(i),cls=c,visible=int(v),enabled=int(e),rect=r,text=t) for h,i,c,v,e,r,t in re.findall(r'^dialog_control hwnd=(\d+) id=(-?\d+) class=(\S+) visible=(\d+) enabled=(\d+) rect=(\S+) text=(.*)$',runner,re.M)]
checks=dict(cleanup=read('review001.json')['passed'],sequence_submitted='input_sequence_submitted=1\n' in runner,cancel_submitted='dialog_cancel_submitted=1\n' in runner,one_save_dialog=sum(c['cls']=='#32770' and c['text']=='Save Game' and c['visible'] and c['enabled'] for c in controls)==1,one_filename_edit=sum(c['cls']=='Edit' and c['id']==1148 and c['visible'] and c['enabled'] for c in controls)==1,one_save_button=sum(c['cls']=='Button' and c['id']==1 and c['text']=='&Save' and c['visible'] and c['enabled'] for c in controls)==1,park_region_unchanged=changed==0)
passive=Path('C:/xwn578/pc001/phase1/auto-1792405399255431899.png');assert Image.open(passive).size==(800,600)
r=dict(passed=all(checks.values()),checks=checks,captures=captures,changed_park_pixels=changed,roi=[5,40,635,430],passive_image=dict(path=str(passive),sha256=sha(passive)),visual_observation='Save Game modal is visible above the paused park, Saved Games folder, selected Forest Frontiers.SV4 filename, Save and Cancel buttons. After Escape the same park view returns.',verified_control_identity=dict(dialog_class='#32770',dialog_title='Save Game',filename_edit_id=1148,save_button_id=1,cancel_button_id=2),filename_text_from_enumeration='empty; cross-process GetWindowText did not read the edit text, so next helper must independently read back the actual filename',saved_game_created=False,physical_access=False,limits='PC dialog inspection and cancellation only; no save/reload or Xbox result. Exact child HWND values are transient and must not be reused.')
out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(checks))
