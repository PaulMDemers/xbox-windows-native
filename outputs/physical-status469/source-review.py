"""Pin primary upstream status definitions; read-only, no console operation."""
import hashlib,json,urllib.request,datetime
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('C:/xwn469/source001');out=K/'status-source-review.json'
assert not P.exists() and not out.exists();P.mkdir(parents=True)
sources=[]
for repo,path in [('torvalds/linux','drivers/i2c/busses/i2c-amd756.c'),('xemu-project/xemu','hw/xbox/amd_smbus.c')]:
 def get(url):
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'xbox-windows-native-source-review'}),timeout=20) as f:
   b=f.read(1024*1024+1);assert len(b)<=1024*1024;return b
 commit=json.loads(get(f'https://api.github.com/repos/{repo}/commits?path={path}&per_page=1'))[0]['sha']
 url=f'https://raw.githubusercontent.com/{repo}/{commit}/{path}';data=get(url)
 dest=P/Path(path).name;dest.write_bytes(data)
 text=data.decode();assert '#define GS_HST_STS' in text and '(1 << 3)' in text
 assert '#define GS_SMB_STS' in text and '(1 << 11)' in text
 sources.append(dict(repository=repo,commit=commit,path=path,url=url,private_file=str(dest),bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
r=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),sources=sources,physical_status=0x808,
 known_busy_mask=0x808,observed_status_contains_error_bits=False,
 conclusion='Existing marker wrongly rejects host-busy bit3 while waiting for its own transaction.',
 original_boot_failure_explained=False,physical_completion_or_recovery_not_observed=True,
 xemu_upstream='Transactions complete synchronously; busy bit definitions exist but this path does not set them.',
 exact_used_emulator_source_binary_identity_not_requalified=True,
 next='New marker must WAIT with existing bounds on either busy bit; do not treat busy as success or clear errors.')
out.write_text(json.dumps(r,indent=2)+'\n')
