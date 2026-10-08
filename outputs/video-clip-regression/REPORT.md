# Matched complex clipping runs pass

RAM0110 control001 and RAM0112 candidate001 both CLOSED with strict ordinary
qualification and upload attribution PASS. Same immutable parent,probe134,startup,
settings and protected payloads; only the display DLL differs. The control uses
the frozen qualified0110 binary;0112 was freshly built from that exact source tree.
All18 cold images are byte-identical across both runs and match independent host
oracles. Each run compares1,769,472 RGB pixels. Three repetitions agree exactly.

| Region / operation | RAM0110 bytes | RAM0112 bytes |
| --- | ---: | ---: |
| Two distant16x16 islands | 122,304 | 2,048 |
| Overlapping rectangles | 4,096 | 3,584 |
| Two partly offscreen rectangles | 393,216 | 1,472 |
| Empty visible intersection | 0 | 0 |
| Sixty4x4 islands | 109,120 | 3,840 |
| Two consecutive draws of the distant islands | 244,608 | 4,096 |
| All18 samples | 2,620,032 | 45,120 |

Actual candidate copies correspond exactly to the visible region pixels,including
the repeated operation. Empty clipping invokes no upload. Callbacks are unchanged:
18 BitBlt callbacks per run. Five actual-result mutations are rejected by the pair
verifier. Counter intervals are quiet outside the measured draw; live DIB reference
rendering causes no primary-driver callback changes.

Both returned normally to the dashboard. Each full allocation scan is clean:
327 directories,6779 files,328 directory clusters,zero errors/orphans. Five hives
parse structurally; protected and installed payloads,startup,pagefile and expected
configuration are unchanged. Zero warning/error/application event deltas. No gate
waiver,debugger,device-policy change or physical access.

Control accepted2026-10-08T04:01:09.780327UTC; candidate04:03:44.270219UTC.
Control preparation21724/runner52532/supervisor46056/audit82751 and candidate
preparation52529/runner88505/supervisor63827/audit48801 CLOSED. Never relaunch or
recollect. Broader GDI/cursor/reset evidence is separate in video-clip-gdi. These
are transfer-volume results,not physical FPS or actual window-drag timing.
