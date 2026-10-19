"""MIT. Apply pre-existing PC584 mutable-file contract; preserve failed review002."""
import hashlib,json,runpy
from pathlib import Path
K=Path(__file__).resolve().parent
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
old=json.loads((K/'final001.json').read_text())
assert old['closed'] and not old['passed']
assert [k for k,v in old['checks'].items() if not v]==['all_502_assets_unchanged']
policy=K.parent/'rct584/integration_review001.py'
assert "set(['game/Data/CSS0.DAT','game/Data/Game.cfg'])" in policy.read_text()
historical=json.loads((K.parent/'rct584/integration-review001.json').read_text())
assert historical['checks']['only_expected_game_mutations']
source=(K/'close_review002.py').read_text()
source=source.replace("out=K/'final001.json'","out=K/'final002.json'")
oldline="checks['all_502_assets_unchanged']=len(assets)==502 and all(all(m['xwn586-kit/'+name.lower()]['sha256']==row['sha256'] for name,row in assets.items()) for m in manifests[1:])"
assert oldline in source
source=source.replace(oldline,"""mutable={'game/Data/CSS0.DAT','game/Data/Game.cfg'}
checks['all_500_immutable_assets_unchanged']=len(assets)==502 and all(all(m['xwn586-kit/'+name.lower()]['sha256']==row['sha256'] for name,row in assets.items() if name not in mutable) for m in manifests[1:])
checks['documented_mutable_files_retained']=all(all('xwn586-kit/'+name.lower() in m for name in mutable) for m in manifests[1:])""")
source=source.replace("'phase1-observations001.json']","'phase1-observations001.json','final001.json','asset-postrun-differences001.json']")
dest=K/'close_review003.py';assert not dest.exists();dest.write_text(source)
receipt=K/'review-correction001.json';assert not receipt.exists()
receipt.write_text(json.dumps(dict(reason='Review002 incorrectly required all pre-launch files to remain immutable. Existing PC584 contract separately retains CSS0.DAT and Game.cfg mutations; no new exception or runtime change.',
 original_failed_review_sha256=sha(K/'final001.json'),original_script_sha256=sha(K/'close_review002.py'),
 existing_policy_sha256=sha(policy),existing_result_sha256=sha(K.parent/'rct584/integration-review001.json'),
 corrected_script_sha256=sha(dest),runtime_reopened=False,recollected=False),indent=2)+'\n')
runpy.run_path(str(dest),run_name='__main__')
