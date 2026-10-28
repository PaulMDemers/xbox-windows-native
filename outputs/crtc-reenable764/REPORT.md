# Test764: kernel CR17 forward-enable control

Prepared from source-only closed762 after native763 closed PASS. Adds precisely
the next original CR17 bit7 enable after laterCR02. Fresh capture63, targete3,
six horizontal neighbors, own saved-value undo63 before older recovery. Outer
blanking stays applied. No later vertical/pitch/PLL/encoder changes or CR1b/22/33
writes. Final pass requires all eleven aggregate recovery masks clear.

Validation PASS:228 actual COFF cases,2353 layout cases,10 clock cases,
independent source/schema/linked checks. Prior same-value CR02 drop limitations
are retained. Frozen source bytes match Git index. Unique E stage/readback PASS.
XBE SHA256 b3d34ababa0920fe0ef9cb258d295a84acc30d1da1c2dd949c8bd98593fca587.
No physical launch yet; no hook, native handoff, Windows or owned VM/process.

Result200words/800bytes. A future native counterpart ends5420 and must expand
the previous initialized5400 boundary with independent bounds/CPU/integration
checks before use. This kernel result does not qualify native mode switching.

Single launch accepted04:15:26UTC; collection/audit pending.
