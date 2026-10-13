"""Describe actual within-boot measurements, never emulator-to-hardware speedup."""
import hashlib,json,statistics
from pathlib import Path
K=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text())
dest=K/'measurement-summary.json';assert not dest.exists()
final=read(K/'final-review.json');a=read(K/'physical001/audit.json')
assert final['scoped_passed'] and final['integrity_passed'] and final['normal_shutdown_count']==1
assert len(a['large_samples'])==5 and all(x['passed'] for x in a['large_samples'])
rows=[]
for ident in range(15):
 group=[x['cases'][ident] for x in a['large_samples']]
 first=group[0]
 assert all((x['size'],x['kind'])==(first['size'],first['kind']) for x in group)
 ms=[x['elapsed_ms']/x['operations'] for x in group]
 ops=[1000/x for x in ms]
 w,h=first['size']
 rows.append(dict(size=[w,h],kind=first['kind'],samples=5,
  median_ms_per_operation=statistics.median(ms),min_ms_per_operation=min(ms),max_ms_per_operation=max(ms),
  median_operations_per_second=statistics.median(ops),
  median_affected_megapixels_per_second=statistics.median(ops)*w*h/1e6,
  raw=[{n:x[n] for n in ['operations','elapsed_ms','global_uploads','global_copied_bytes','minimum_workload_bytes']} for x in group]))
fits=[]
for kind in ['fill','ram_upload','overlap_down_right','overlap_up_left','wm_paint']:
 group=[x for x in rows if x['kind']==kind];xs=[x['size'][0]*x['size'][1] for x in group];ys=[x['median_ms_per_operation'] for x in group]
 xm=statistics.mean(xs);ym=statistics.mean(ys)
 slope=sum((x-xm)*(y-ym) for x,y in zip(xs,ys))/sum((x-xm)**2 for x in xs)
 intercept=ym-slope*xm;residual=sum((y-(intercept+slope*x))**2 for x,y in zip(xs,ys));total=sum((y-ym)**2 for y in ys)
 fits.append(dict(kind=kind,ms_per_megapixel=slope*1e6,intercept_ms=intercept,
  descriptive_r_squared=1-residual/total if total else None,
  limits='Three area medians within one boot; descriptive only, no causal or repeat-boot inference.'))
r=dict(physical=True,rows=rows,area_fits=fits,strict_passed=final['strict_passed'],
 scoped_passed=True,changed_rendering_driver=False,independent_boot_replications=1,
 included_in_time=['GDI operation','GdiFlush','message dispatch','visibility checks'],
 excluded_from_time=['allocation','resize','pixel/source/guard oracle','stats snapshots','logging'],
 limits='Affected pixels are logical work, not measured memory-bus bandwidth. No desktop FPS, GPU acceleration or performance improvement claim. Five samples share one boot.',
 pins={n:hashlib.sha256((K/n).read_bytes()).hexdigest() for n in ['final-review.json','physical001/audit.json']})
dest.write_text(json.dumps(r,indent=2)+'\n')
for row in rows:print('%s %sx%s %.3f ms/op (%.1f ops/s)'%(row['kind'],*row['size'],row['median_ms_per_operation'],row['median_operations_per_second']))
