"""Independent RGB comparison of a fixed interior scenery region."""
ROI=(160,80,620,440)
def compare(a,b):
 assert a.size==b.size==(640,480),'wrong frame dimensions'
 assert a.mode==b.mode=='RGB','expected decoded RGB'
 aa=a.crop(ROI).tobytes();bb=b.crop(ROI).tobytes();assert len(aa)==len(bb)==165600*3
 changed=sum(aa[i:i+3]!=bb[i:i+3] for i in range(0,len(aa),3))
 return dict(changed_pixels=changed,total_pixels=165600,exact=changed==0)
def qualify(reference,before,moved,loaded,stable):
 rows=dict(before_to_moved=compare(before,moved),moved_to_loaded=compare(moved,loaded),
 loaded_to_reference=compare(loaded,reference),loaded_to_stable=compare(loaded,stable))
 return dict(passed=rows['before_to_moved']['changed_pixels']>50000 and rows['moved_to_loaded']['changed_pixels']>50000 and
 rows['loaded_to_reference']['exact'] and rows['loaded_to_stable']['exact'],roi=ROI,comparisons=rows)
