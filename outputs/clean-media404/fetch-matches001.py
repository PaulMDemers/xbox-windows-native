"""Download exact catalog matches into a fresh private folder, then compare supplied bytes."""
import concurrent.futures,hashlib,json,time,urllib.parse,urllib.request
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn404/downloads001');P.mkdir(parents=True,exist_ok=False)
rows=[('retail','en_win2000_pro_sp4','en_win2000_pro_sp4.iso','EN_WIN2000_PRO_SP4.ISO',386859008),('customized','windows-2000-sp-4','Windows 2000 (SP4).iso','Windows 2000 (SP4).iso',594280448)]
def one(row):
 label,item,name,local,size=row;dest=P/(label+'.iso');url='https://archive.org/download/'+item+'/'+urllib.parse.quote(name)
 r={'label':label,'url':url,'local_supplied_name':local,'expected_bytes':size,'status':'downloading','started_unix':time.time()};deadline=time.monotonic()+900;last=time.monotonic()
 try:
  with urllib.request.urlopen(url,timeout=30) as remote,dest.open('xb') as f:
   assert urllib.parse.urlparse(remote.url).hostname.endswith('archive.org')
   r['final_url']=remote.url;h=hashlib.sha256();h1=hashlib.sha1();count=0
   while chunk:=remote.read(1024*1024):
    count+=len(chunk);assert count<=size and time.monotonic()<deadline;f.write(chunk);h.update(chunk);h1.update(chunk)
    if time.monotonic()-last>30:print(label,count,'/',size,flush=True);last=time.monotonic()
  assert count==size
  with dest.open('rb') as f:readback=hashlib.file_digest(f,'sha256').hexdigest()
  with (W/'outputs'/local).open('rb') as f:supplied=hashlib.file_digest(f,'sha256').hexdigest()
  assert readback==h.hexdigest()==supplied
  r.update(status='full_download_readback_exact_match',bytes=count,sha256=h.hexdigest(),sha1=h1.hexdigest(),private_download=str(dest),same_bytes_as_supplied=True,setup_validation_inherited_only_if_supplied_case_passes=True)
 except Exception as e:r.update(status='failed',error=type(e).__name__+': '+str(e),partial_bytes=dest.stat().st_size if dest.exists() else 0)
 r['finished_unix']=time.time()
 with (K/('online-'+label+'001.json')).open('x') as f:json.dump(r,f,indent=2)
 print(label,r['status'],flush=True);return r
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(one,rows))
print(json.dumps([{k:r.get(k) for k in ['label','status','bytes','sha256']} for r in results]))
