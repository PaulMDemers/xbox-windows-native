# Physical copy fast path is correct, but shows no material speed benefit

The fresh OFF/ON physical pair completed at 1920×1080. Both passed all five
graphics samples, independent pixels/guards and scanout comparison, exact
eligible-byte coverage, audio API/device identity/joins, normal shutdown and
cold integrity checks. The candidate used the fast path for every eligible
call and byte. This did **not** materially reduce observed copy time.

Median milliseconds per operation across five samples:

| Copy size and direction | Control wall time | Candidate wall time |
|---|---:|---:|
| 256×128 down/right | 2.072 | 2.049 |
| 256×128 up/left | 2.308 | 2.322 |
| 640×360 down/right | 17.045 | 17.045 |
| 640×360 up/left | 17.857 | 17.857 |
| 960×540 down/right | 40.263 | 40.263 |
| 960×540 up/left | 40.263 | 40.263 |

For the largest copies, the selected copy body changed from 15.653 to
15.547 ms down/right and 16.109 to 15.891 ms up/left. Upload remained about
24.2–24.3 ms. These are global elapsed counters from sequential boots, not
isolated CPU cycles or desktop FPS. No performance qualification or driver
promotion follows from small differences of this size.

Control launched at 18:26:07 UTC and returned at 18:34:21; candidate launched
at 18:38:50 and returned at 18:46:56 on October 13. Normal startup was restored
first after each return, followed by the original display driver. All four
read-only E allocation scans passed with zero errors/orphans. Final E totals
were 640 directories, 7,629 files and 657 directory clusters. Five structural
hives, selected bindings/policies, protected E files, original F Windows and
loader, and event/setup history passed their checks. Final closeout rehashed
1,320 captured files per case, the scanner captures and all 210 frozen inputs.

**Combined and strict qualification remain FALSE.** Each boot retained
Ftdisk49 on HarddiskVolume1 and Srv2013 for Windows F: during the combined
interval. No warning, service or gate was suppressed. Graphics/audio API
completion is distinct from overall qualification and from user audibility.
This is not a whole-disk file-content or crash-dump qualification.

The console is back at UnleashX with normal startup and original E display
driver `b23b94ac12c9f507e3d905d9de905dcff9a8fd53c2fba4336fb830e97666101d`
verified again after the final scan. No tool accessed console C. Original F
rollback, immutable tags and the paused automation remain unchanged. Both
Windows launches and all four scans are closed and consumed; do not repeat,
recollect or use executed disks as new test parents.
