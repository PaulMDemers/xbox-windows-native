"""MIT. Private screen comparisons support, but do not replace, visual observations."""
from pathlib import Path
import hashlib,json
from PIL import Image,ImageChops
K=Path(__file__).resolve().parent; P=Path('C:/xwn568/pc001/phase1')
out=K/'observations001.json'; assert not out.exists()
cases=[
 ('window_edge_right','1792393900346462257','1792393918450836507',(40,90,670,480),'View stayed still'),
 ('window_arrow_right','1792393918450836507','1792393930932188735',(40,90,670,480),'Landscape moved'),
 ('window_right_drag','1792393930932188735','1792393942414684999',(40,90,670,480),'Landscape moved'),
 ('fullscreen_edge_right','1792394024108920445','1792394037348192916',(5,35,635,440),'Landscape moved'),
 ('fullscreen_arrow_left','1792394037348192916','1792394056361355985',(5,35,635,440),'Landscape moved'),
 ('fullscreen_right_drag','1792394056361355985','1792394067185466559',(5,35,635,440),'Landscape moved')]
rows=[]
for name,b,a,roi,observation in cases:
    bp=P/('screen-'+b+'.png');ap=P/('screen-'+a+'.png')
    before=Image.open(bp).convert('RGB');after=Image.open(ap).convert('RGB');assert before.size==after.size
    diff=ImageChops.difference(before.crop(roi),after.crop(roi));count=sum(px!=(0,0,0) for px in diff.get_flattened_data())
    rows.append(dict(case=name,observation=observation,screen_size=list(before.size),roi=list(roi),changed_pixels=count,pixels=diff.width*diff.height,before=dict(path=str(bp),sha256=hashlib.sha256(bp.read_bytes()).hexdigest()),after=dict(path=str(ap),sha256=hashlib.sha256(ap.read_bytes()).hexdigest())))
assert rows[0]['changed_pixels']==0
r=dict(scope='Fresh PC control568; visual landscape movement plus separate pixel comparisons, not a rate or Xbox result',game='Unmodified Deluxe, Forest Frontiers',edge_option_enabled_both_modes=True,desktop='Changed through Display Properties from640x480 to800x600 so the640x480 game client fits',game_modes=['Window','Full Screen640x480','Window restored'],pause_button_clicked=True,sound_tested=False,physical_access=False,setup_notes=['Getting Started and the game occluded the Run dialog; inputs checked visually before execution','Run dialog displayed D:PREP.CMD; resolved to helper CD root and copied502 files plus runner','Initial Options click missed menu; corrected after checking screen'],cases=rows,limitations=['Only right-edge dwell tested, not all four edges','Arrow directions and drag trajectories differ between modes; movement qualification only','Pixel change alone does not prove camera movement; visual landscape displacement also observed','No performance, cross-restart save persistence, audio or GPU claim'])
out.write_bytes((json.dumps(r,indent=2)+'\n').encode());print([(x['case'],x['changed_pixels']) for x in rows])
