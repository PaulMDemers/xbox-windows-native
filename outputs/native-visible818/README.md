# Native visible818: combined720x480 diagnostic

Fresh source-only704 encoder/VGA flow plus qualified817 preserving changes.
The existing720p baseline and ordinary Windows launcher are untouched.

Expected: blue-topped720p preparation for5 seconds, blank transition, then
720x480 authored white border/green top/red-green-blue-white quadrants and a
checker patch near the bottom. Holds deliberately. Any postblank failure makes
one bounded reblank request and holds. No runtime retry or firmware restoration.
A returning dashboard can be kernel refusal; it is not native success.

Host validation:881 full transaction cases,32770 bounds,16 relocated integration
cases,12 fresh CPU contexts/refusals(all VMs closed),164177 plan cases,45+46
compiled page checks,418 compiled ownership checks, exact object/PE/XBE bytes.
The complete emulator model validates bus order and pixels, not real encoder
operation, physical timing or Windows. Integration001/002 time limits in the
instrumented drawing loop and link-review012 incomplete section enumeration
are preserved. Integration003 uses stack-write monitoring and passes. Link013
includes all49 relocations including four rodata callbacks.

Private binaries remain C:/xwn818. No startup hook, Windows or3D in this test.
