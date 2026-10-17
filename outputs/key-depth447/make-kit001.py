"""Create a new 24-bit desktop control; closed446 remains immutable."""
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];old=K.parent/'key-semantics446'
names=['build001.py','binary-review001.py','prepare001.py','cold002.py','cold003.py','login001.py','run001.py','independent001.py','preflight001.py','review001.py','actual-controls001.py','closeout001.py']
for name in names:
    p=K/name;assert not p.exists()
    s=(old/name).read_text(encoding='utf-8').replace('key-semantics446','key-depth447').replace('xwn446','xwn447').replace('XWN446','XWN447').replace('run446','run447')
    if name=='build001.py':
        s=s.replace('key-depth447-build001/keyprobe.exe','key-semantics446-build001/keyprobe.exe')
    elif name=='preflight001.py':
        s=s.replace("'gate-tests001.json'","'inherited-gate-tests001.json'")
        s=s.replace("assert json.loads((K/'inherited-gate-tests001.json').read_text())['passed'] is True", "gate=json.loads((K/'inherited-gate-tests001.json').read_text());assert gate['passed'] is True and gate['gate_sha256']==sha(K/'launch_gate.py')\nassert json.loads((K/'mode-tests001.json').read_text())['passed'] is True")
        s=s.replace("'inherited-gate-tests001.json']]","'inherited-gate-tests001.json','mode-tests001.json']]")
    elif name=='review001.py':
        s=s.replace('from launch_gate import sha','from launch_gate import sha\nfrom mode_receipt import validate_mode')
        s=s.replace("runner['schema']=='446'","runner['schema']=='447'")
        s=s.replace("record=dict(runner=runner,rows=[],scope='Actual NT5 raw RGB32 diagnostic; no display-mode change or hardware access')", "mode_review=validate_mode(runner)\nrecord=dict(runner=runner,mode_review=mode_review,rows=[],scope='Actual NT5 RGB32 diagnostic on temporary enumerated24-bit desktop; no hardware access')")
        s=s.replace('review=g.validate(raw,src,dst,backend,code)','review=g.validate(raw,src,dst,backend,code)\n assert review[\'desktop\']==dict(width=640,height=480,bpp=24)')
        pos=s.index('print(json.dumps(dict(all_semantics_passed=')
        s=s[:pos]+"print(json.dumps(dict(all_semantics_passed=record['all_semantics_passed'],rows=[dict(backend=r['backend'],mismatches=r['review']['mismatches'],desktop=r['review']['desktop']) for r in record['rows']]),indent=2))\n"
    elif name=='closeout001.py':
        s=s.replace("'Keyed pixel failures remain failures'","'This24-bit desktop is not a32-bit desktop match'")
    p.write_text(s,encoding='utf-8',newline='\n')
for src,dst in [('launch_gate.py','launch_gate.py'),('gate-tests001.json','inherited-gate-tests001.json'),('sample-build001.json','sample-build001.json')]:
    (K/dst).write_bytes((old/src).read_bytes())
s=(old/'runner.c').read_text(encoding='utf-8').replace('xwn446','xwn447').replace('number("schema",446)','number("schema",447)')
s=s.replace('static HANDLE log_file;','static HANDLE log_file;\nstatic DEVMODEA original_mode,requested_mode,observed_mode;\nstatic int mode_changed,mode_restored;')
anchor='void WINAPI mainCRTStartup(void)'
mode='''static void mode_fields(const char *prefix,const DEVMODEA *d){char key[80];
    wsprintfA(key,"%s_bits",prefix);number(key,d->dmBitsPerPel);
    wsprintfA(key,"%s_width",prefix);number(key,d->dmPelsWidth);
    wsprintfA(key,"%s_height",prefix);number(key,d->dmPelsHeight);
    wsprintfA(key,"%s_hz",prefix);number(key,d->dmDisplayFrequency);
    wsprintfA(key,"%s_flags",prefix);number(key,d->dmDisplayFlags);
}
static int enter_mode(void){unsigned n,found=0,index=0;LONG status;
    zero(&original_mode,sizeof(original_mode));original_mode.dmSize=sizeof(original_mode);
    if(!EnumDisplaySettingsA(0,ENUM_CURRENT_SETTINGS,&original_mode)){number("mode_query_failed",1);return 0;}
    mode_fields("mode_original",&original_mode);
    if(original_mode.dmPelsWidth!=640||original_mode.dmPelsHeight!=480||original_mode.dmBitsPerPel!=16||original_mode.dmDisplayFrequency!=60||original_mode.dmDisplayFlags!=0){number("mode_original_mismatch",1);return 0;}
    for(n=0;n<4096;n++){
        zero(&observed_mode,sizeof(observed_mode));observed_mode.dmSize=sizeof(observed_mode);
        if(!EnumDisplaySettingsA(0,n,&observed_mode))break;
        if(!found&&observed_mode.dmPelsWidth==640&&observed_mode.dmPelsHeight==480&&observed_mode.dmBitsPerPel==24&&observed_mode.dmDisplayFrequency==60&&observed_mode.dmDisplayFlags==0){requested_mode=observed_mode;found=1;index=n;}
    }
    number("mode_inventory_count",n);number("mode_inventory_complete",n<4096);number("mode_selected",found);
    if(n==4096||!found)return 0;
    number("mode_selected_index",index);mode_fields("mode_requested",&requested_mode);
    requested_mode.dmFields=DM_BITSPERPEL|DM_PELSWIDTH|DM_PELSHEIGHT|DM_DISPLAYFREQUENCY|DM_DISPLAYFLAGS;
    status=ChangeDisplaySettingsA(&requested_mode,CDS_TEST);number("mode_test_status",(DWORD)status);if(status!=DISP_CHANGE_SUCCESSFUL)return 0;
    status=ChangeDisplaySettingsA(&requested_mode,0);number("mode_apply_status",(DWORD)status);if(status!=DISP_CHANGE_SUCCESSFUL)return 0;mode_changed=1;
    zero(&observed_mode,sizeof(observed_mode));observed_mode.dmSize=sizeof(observed_mode);
    if(!EnumDisplaySettingsA(0,ENUM_CURRENT_SETTINGS,&observed_mode)){number("mode_active_query_failed",1);return 0;}
    mode_fields("mode_active",&observed_mode);
    if(observed_mode.dmPelsWidth!=640||observed_mode.dmPelsHeight!=480||observed_mode.dmBitsPerPel!=24||observed_mode.dmDisplayFrequency!=60||observed_mode.dmDisplayFlags!=0){number("mode_active_mismatch",1);return 0;}
    return 1;
}
static void leave_mode(void){LONG status;
    number("mode_changed",mode_changed);if(!mode_changed)return;
    original_mode.dmFields=DM_BITSPERPEL|DM_PELSWIDTH|DM_PELSHEIGHT|DM_DISPLAYFREQUENCY|DM_DISPLAYFLAGS;
    status=ChangeDisplaySettingsA(&original_mode,0);number("mode_restore_status",(DWORD)status);
    zero(&observed_mode,sizeof(observed_mode));observed_mode.dmSize=sizeof(observed_mode);
    if(!EnumDisplaySettingsA(0,ENUM_CURRENT_SETTINGS,&observed_mode)){number("mode_restore_query_failed",1);return;}
    mode_fields("mode_after_restore",&observed_mode);
    mode_restored=status==DISP_CHANGE_SUCCESSFUL&&observed_mode.dmBitsPerPel==original_mode.dmBitsPerPel&&observed_mode.dmPelsWidth==original_mode.dmPelsWidth&&observed_mode.dmPelsHeight==original_mode.dmPelsHeight&&observed_mode.dmDisplayFrequency==original_mode.dmDisplayFrequency&&observed_mode.dmDisplayFlags==original_mode.dmDisplayFlags;
    number("mode_restored",mode_restored);
}
'''
assert s.count(anchor)==1;s=s.replace(anchor,mode+anchor)
s=s.replace('    for(i=0;i<2;i++){','    if(!enter_mode())goto done;\n    for(i=0;i<2;i++){')
s=s.replace('done:\n    number','done:\n    leave_mode();\n    number').replace('ExitProcess(completed==2?0:1)','ExitProcess(completed==2&&mode_restored?0:1)')
(K/'runner.c').write_text(s,encoding='utf-8',newline='\n')
print('Created new447 controller/kit; exact446 probe and launch gate retained.')
