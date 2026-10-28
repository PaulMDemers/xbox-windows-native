# Kernel CR03 checkpoint754

Closed750 source reused; native752 physical CR02 result qualified. Add only the
next original CR03 write from pinned gpu_legacy.c line58. Actual752 preparation
CR03=8c. Preserve own upper3bits; ((779/8)-1)&31=0 makes target80. The captured
baseline is an admission guard, never a replacement recovery value. Full-byte
CR03 and CR00/02/04/05 neighbors checked. Restore own CR03 before CR02/00/05/04,
then H7 and preserving prefix. Timing recovery failure inhibits output/drawing.

143words572bytes; previous133 unchanged. New133..142: before,target,attempt,
after,restored,mask,CR00/02/04/05 afterCR03. New75312 forward mismatch and75313
recovery failure; CR03 recovery precedes CR02 and selector mismatch remains last.
No later CR05 bit7, CR17/01, pitch, vertical, encoder, PLL or scanout write added.
Automatic kernel return, no native handoff/Windows/full mode switch proof.

753 clock refusal is preserved and closed.754 uses token-aware namespace
replacement and correct3375000 guard, with both64-bit halves logged. Ten actual
main.obj clock-fragment cases validate argument preservation and strict64-bit
admission, including wrong3375300/3375400 and nonzero-high refusals. Independent
main source comparison starts from qualified750 with token-aware replacement;
constants3375000 and all layout code are checked separately. CR03 unchanged.
