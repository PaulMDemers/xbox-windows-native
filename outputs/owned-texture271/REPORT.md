#271: owned graphics control compiled and checked, no guest launch

The new standalone nxdk control allocates four immutable textures, draws them,
disables them through a real flat draw, stops at a compiled checkpoint and draws
them again after resumption. It captures independent framebuffer and guard results
and has bounded application waits. It does not install a release helper, modify
Windows drivers, use the physical Xbox or establish native GPU ownership.

Reviewed build005 is at E:/xwn271/build005. Its XBE SHA256 is
4ada3d6c337360d14f67b6fe88ee8d42640a22849f6b2d310d884ef04a41dec1.
Binary review confirms the19-byte checkpoint, four actual callers,1612-byte state,
all four texture shader stages and explicit constants/attribute setup. All49
actual SDK headers were frozen and verified before/after compilation;49 SDK
source/library/tool pins remained unchanged. Build lease and20GiB projected C
guard were used. No guest fixture or emulator process was created.

The independent host oracle matched16,384 source/guard bytes using exact extracted
guest functions under ASan/UBSan. It defines720 expected framebuffer bytes per
capture and rejects1,456 synthetic pixel/metadata mutations. This does not prove
actual guest pixels, texture lifetimes or a performance improvement.

Preserved development failures and superseded artifacts:

- Initial Windows PowerShell invocation refused the script before execution.
  Process-local execution policy was specified for reviewed build scripts; no
  machine/user policy changed.
- Build001 failed C compilation on SDK MAXRAM redefinition and DWORD pointer type.
- Build002 compiled but warning review rejected an additional linker merge
  diagnostic. Its generated vertex constant was not explicitly initialized.
- Build003 passed compilation after constant and warning review; further source
  review found that the flat shader did not clear previous texture stages and
  texture outputs needed explicit projective z/w. It was never launched.
- Build004 fixes both shader-state issues. Build005 repeats those identical native
  inputs with the full discovered header closure frozen before compilation.
- The first binary reviewer expected three checkpoint calls; compiler inlining
  produced a fourth early-error call. Original checker and failure are preserved.
- Oracle002 accidentally retained oracle001's compiler/output path. Review caught
  it; the original001 files, including the rewritten binary, remain byte-exact.
  That attempt is not used as a fresh-capsule qualification. Corrected oracle003
  uses a wholly new directory and is the authoritative result. All older inputs
  and results are retained.

Next build the bounded homebrew runtime attestor/controller, then run one new
owned no-release pixel control. Only actual unchanged four-generation observation
can support a later matched release candidate. Existing270 host accounting and
263 scoped pixel results remain separate;269 remains failed/truncated. Physical
audio004/softwarevideo118/shared158/FATX0101, recovery256,0.1.0 and0088 are unchanged.
