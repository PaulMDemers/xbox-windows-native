"""Create a fresh matched UC-store kit; never mutate historical evidence."""
import ast, json, shutil
from pathlib import Path

k = Path(__file__).resolve().parent
ws = k.parents[1]
old = k.parent / 'video-text-clip205'
assert not (k / 'build.py').exists()
for name in ['build.py', 'Build.ps1', 'review-build.py']:
    s = (old / name).read_text(encoding='utf-8')
    s = s.replace('video-text-clip205-001', 'video-scalar208-001')
    if name == 'build.py':
        s = s.replace("clipprofile=read(k/'source-review.json')", "clipprofile=read(k.parent/'video-text-clip205/source-review.json')")
        s = s.replace("k/'0118-text-input-clip.patch'", "k.parent/'video-text-clip205/0118-text-input-clip.patch'")
        s = s.replace("defs['XWN_UC_STORES']='OFF'", "defs['XWN_UC_STORES']=enabled")
        s = s.replace("defs['XWN_TEXT_BOUNDS']=enabled", "defs['XWN_TEXT_BOUNDS']='OFF'")
    if name == 'review-build.py':
        s = s.replace("s=read(k/'source-review.json')", "s=read(k.parent/'video-text-clip205/source-review.json')")
        s = s.replace("k/'0118-text-input-clip.patch'", "k.parent/'video-text-clip205/0118-text-input-clip.patch'")
        s = s.replace("k/'display'", "k.parent/'video-text-clip205/display'")
        s = s.replace("k/'display/", "k.parent/'video-text-clip205/display/")
        s = s.replace("da.pop('XWN_TEXT_BOUNDS')", "da.pop('XWN_UC_STORES')").replace("db.pop('XWN_TEXT_BOUNDS')", "db.pop('XWN_UC_STORES')")
        s = s.replace("da['XWN_BODY_PROFILE']==da['XWN_UC_STORES']=='OFF'", "da['XWN_BODY_PROFILE']==da['XWN_TEXT_BOUNDS']=='OFF'")
        s = s.replace("only_definition_difference='XWN_TEXT_BOUNDS'", "only_definition_difference='XWN_UC_STORES'")
    if name.endswith('.py'): ast.parse(s)
    (k / name).write_text(s, encoding='utf-8', newline='\n')
(k / 'DESIGN.md').write_text('''# Fresh scalar UC-store comparison208

Reconstruct the reviewed118 source tree independently. The only paired build
definition difference is XWN_UC_STORES OFF/ON. Text bounds and body clocks stay
OFF in both. Preserve row alignment/nonoverlap eligibility, fallback, clip,
ownership, cache and allocation behavior. Reuse exact206 v11 probe, joined202
runner and201 helper in fresh209 cases, with all pixel/row/idle/cold/event gates.
This is not a retry of held187; candidate187 remains never launched.

Pin compiled ordered scalar stores and baseline REP MOVSD. Independent historical
184 row-store host tests remain attributable to their exact source; no new test
run is fabricated. Fixed-work per-operation timings and unchanged readback control
are descriptive until actual hardware evidence and background/run-order limits
are assessed. Broad window counters are not desktop FPS. No promotion/release or
physical storage qualification; baseline0093/0101 is restored after each trial.
''', encoding='utf-8')
print('New208 paired build protocol prepared; no launch')
