# Preserve actual readback for native movement failure

First window-move/control001 failed18 pixel cases,even after forced redraw,with
normal shutdown and clean integrity/events. Candidate fixture prepared but NEVER
launched. This new probe137 retains same drivers,geometry,drawing and exact gates;
adds cold raw move/readback and redraw/readback files plus parent origin/size.
No driver changes or speculative clipping corrections. New unique child only.
Extra file writes occur outside measured move/redraw intervals. Coarse timing is
not isolated or a physical speed measurement. Preserve any failure without waiver.
