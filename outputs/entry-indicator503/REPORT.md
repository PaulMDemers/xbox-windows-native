# Entry-only indicator prototype503

The proposed kernel-API indicator passes293 host executions plus293 refused
reentries. This is host-only: no XBE build, emulator/console launch, SDK change,
Windows startup hook or physical mutation occurred.

The outer assembly requests amber through the kernel before entering the exact498
file gate. It requests green only after that gate's final flush/close succeeded,
then requests automatic LED mode once and firmware return. This candidate will
return without starting the original preparation or Windows. It preserves original
entry registers/flags and has no raw I/O or interrupt-control instructions.

The test executes the actual proposed i386 assembly, with every Xbox SMBus,delay,
file and firmware service explicitly modeled.199 inherited cases include128 flag
combinations and71 file/cleanup failures.94 added cases cover indicator/delay
failures and combinations. Independent review decodes194 complete receipt files,
rejects99 partial files, verifies the byte-exact498 gate/decoder and original file
model prefix, and checks214 production instructions. A complete receipt alone
still does not prove final flush/close; the decoder was not weakened.

The retained physical307 report identifies kernel1.0.4034.1,size623712 and
timestamp1004048809. Actual502 emulator identity is size636160,timestamp1023192752.
All required ordinals exist in the retained tables at different addresses. This
does not establish an ABI defect or explain501. The old private307 kernel was not
found in checked C/E locations; this review uses its retained metadata, not newly
rehash-verified proprietary bytes.502 public notes' earlier "physical unknown"
means not freshly captured; this historical identity is now explicitly recorded.

The old470 raw SMBus/CLI marker is unsuitable for blind relocation into an active
early kernel context. The proposed indicator uses supported kernel calls instead.
Kernel calls may still block: two-second requested delays and finite call counts
are not an outer execution deadline. Actual LED visibility, API completion,
automatic restoration and dashboard return all need separate runtime evidence.
No original physical failure, including501/497/487, is requalified.

The frozen source comment calls entry503_led's internal convention "cdecl";
its actual callee cleanup is ret8 and is exercised by the host tests. This is a
comment erratum, not an executed code change. All893 private files,9 source pins,
4 compiler tools and8 identity inputs are rehashed. Host session99426 is closed.
See host001.json, kernel-identity001.json, review001.json and final-review.json.
