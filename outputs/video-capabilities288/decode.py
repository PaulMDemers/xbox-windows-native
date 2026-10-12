"""Decode the actual probe log, retaining capability flags versus active AV pack."""
import re

def decode(data):
    lines=[s.strip() for s in data.decode('ascii').splitlines() if s.strip()]
    assert lines[0]=='XWN_VIDEO288 version=1 mode_changes=0'
    assert len(lines)>=7 and lines[-1].startswith('COMPLETE ')
    def fields(prefix, names):
        rows=[s for s in lines if s.startswith(prefix+' ')];assert len(rows)==1
        values=re.findall(r'(\w+)=([0-9a-f]+)',rows[0]);assert [n for n,v in values]==names
        return dict(values)
    video=fields('VIDEO',['settings','scanout','hvalid','vvalid'])
    enc=fields('ENCODER',['conexant_status','conexant_value','focus_status','focus_value'])
    done=fields('COMPLETE',['error','log_ok','modes','mode_changes'])
    assert done['error']=='0' and done['log_ok']=='1' and done['mode_changes']=='0'
    settings=int(video['settings'],16);pack=settings&255
    modes=[]
    for line in lines:
        if line.startswith('MODE '):
            v=list(map(int,line.split()[1:]));assert len(v)==4
            assert 320<=v[0]<=1920 and 200<=v[1]<=1080 and v[2]==32 and v[3] in (50,60)
            assert v not in modes;modes.append(v)
    assert 0<len(modes)<=16 and len(modes)==int(done['modes'])
    conn=int(enc['conexant_status'],16)==0;focus=int(enc['focus_status'],16)==0
    assert not (conn and focus),'Ambiguous encoder responses'
    encoder='Conexant' if conn else 'Focus' if focus else 'Unknown'
    if pack!=4:assert not any(m[1] in (720,1080) for m in modes),'HD mode on non-HDTV pack'
    return dict(encoder=encoder,av_pack_code=pack,av_pack='HDTV/component' if pack==4 else 'standard AV' if pack==1 else 'other/unknown',
        encoder_settings_hex=video['settings'],region_code=(settings>>8)&255,
        saved_flags=dict(p480=bool(settings&0x80000),p720=bool(settings&0x20000),i1080=bool(settings&0x40000)),
        modes=modes,mode_changed=False,hd_mode_exposed=any(m[1]==1080 for m in modes),
        inherited_geometry=[int(video['hvalid'],16)+1,int(video['vvalid'],16)+1],
        limits='AV-pack detection and SDK availability, not EDID, cable-brand identification or electrical 1080i validation. Ignore returned SMBus data on error.')
