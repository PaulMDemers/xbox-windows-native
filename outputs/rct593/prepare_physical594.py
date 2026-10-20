"""MIT. Draft a new controller; no physical access or launch from this generator."""
from pathlib import Path
K=Path(__file__).resolve().parent; T=K.parent/'rct594'
assert not T.exists(); T.mkdir()
(T/'.gitattributes').write_bytes(b'* -text whitespace=cr-at-eol\n')
for name in ['controller001.py','controller_host001.py']:
    source=(K.parent/'rct591'/name).read_text()
    source=source.replace('591','594').replace('xwn589','xwn586').replace('xwn586-kit','xwn593-kit')
    # The installed source is586, while the fresh destination is593.
    source=source.replace('/E/xwn593-kit/owner.json','/E/xwn586-kit/owner.json')
    source=source.replace("old='/E/xwn593-kit/game'","old='/E/xwn586-kit/game'")
    source=source.replace("m.names(f,'/E/xwn593-kit')","m.names(f,'/E/xwn586-kit')")
    if name=='controller_host001.py':
        source=source.replace("'/E/xwn593-kit", "'/E/xwn586-kit")
    source=source.replace('xwn586 goto','xwn593 goto').replace("RESULT='/E/xwn586'","RESULT='/E/xwn593'")
    source=source.replace("{'xwn586','xwn593-kit'}","{'xwn593','xwn593-kit'}").replace("assert 'xwn586' not", "assert 'xwn593' not")
    source=source.replace("if 'xwn586' in", "if 'xwn593' in")
    source=source.replace('run586.exe','run593.exe').replace('native_pc_control=586','native_pc_control=593')
    source=source.replace('pristine_assets_reused_from_closed590=True','retail_assets_and_prior_save_preserved_from_closed592=True')
    if name=='controller001.py':
        start=source.index('def boot_work_closed():');end=source.index('\n\ndef startup',start)
        source=source[:start]+'''def boot_work_closed():
    assert read(K.parent/'rct592/final001.json')['closed']
    assert read(K.parent/'rct593/final001.json')['closed']
    assert read(K.parent/'rct593/save-review001.json')['passed']
    assert read(K.parent/'rct566/transfer001.json')['passed']
'''+source[end:]
    (T/name).write_bytes(source.encode())
for name in ['supervise001.py','observe001.py','audit002.py','registry_review002.py','user_hive_audit001.py','welcome_review001.py']:
    source=(K.parent/'rct592'/name).read_text().replace('592','594').replace('xwn586','xwn593')
    (T/name).write_bytes(source.encode())
(T/'DESIGN.md').write_text('''# RCT594 matched physical save observation

Use the exact PC593-qualified helper once through the ordinary720p launcher.
Move only the owned retail game directory from xwn586-kit to xwn593-kit after
full identity verification. Preserve the prior XWN586.SV4 with the game; never
overwrite it. Restore only catalogued mutable retail config/CSS0 files from
verified pristine assets. No duplicated game installation or driver change.

New output xwn593 and save XWN593.SV4 must be absent. One hook installed last;
one bounded SITE request. On dashboard return remove hook first, cold collect,
compare helper whole-file SHA1/size with the persisted new save, inspect captures,
and audit shutdown/registry/hives. A later Load remains a separate gate.
No cold-start claim, fullscreen, boot investigation, sound or acceleration claim.
''')
print('Drafted594 controller and tests; not packaged or staged')
