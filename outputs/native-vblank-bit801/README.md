# Native CR09 vertical-blank-start bit5 control (Test801)

This candidate derives from the **sources** of closed kernel800 and native799.
It changes CR09 `60 -> 40 -> 60` after the CR12 display-end transaction, checks
eight neighboring fields, and restores its saved CR09 before reversing CR12.
The intended result is a held optical report on the Xbox1.6 with HDMI720p.
It is not a complete mode switch, Windows desktop support, or acceleration.

See `NEXT.md` and the engineering continuation for the current lifecycle state.
An ELF/model/build PASS alone never authorizes interpreting a physical result.

## Active source and checks

- `probe-native.c`: exact kernel800 source with narrowly scoped status renumbering
  and the native CR0/CR3/CR4/IF guard.
- `probe-compact-native.c`: the same hardware operations, with 344 sentinel fields
  initialized through a constant offset table. `compact002.py` records that change.
- `payload_build008.py`: 22,968-byte native ELF/raw payload, padded to23,040 bytes.
- `host_build009.py`: fresh `host007`, using `bridge003.S` and14 absolute relocations.
- `model003.py` / `model004.py`: original and compact actual-ELF execution;
  `equivalence002.py` checks every result, read, write and port trace.
- `integration012.py`: complete relocated handoff path (`integration010.json`).
- `cpu005.py`: fresh diskless CPU contexts and refusals; each owned VM is closed.
- `optical_review005.py`: independent full-framebuffer renderer checks.
- `build012.py`: nxdk `build002`, only after CPU and integration PASS.
- `page_review008.py`, `page_boundary009.py`, `plan_review003.py`,
  `linked_review007.py`, `link_review012.py`, `source_review005.py` and
  `review_prepare007.py`: arithmetic, binary, source, bounds and final pin checks.
- `physical007.py`: unique `E/Applications/XWNMode801`, exact stage/readback,
  one20-second SITE request, no startup hook and no dashboard C access.

Run heavy build/emulator scripts through the existing build/xemu resource leases.
Scripts create unique output receipts and intentionally refuse to overwrite them.
Do not rerun a closed runtime. Reproduction requires new owned attempt paths.

## Memory contract

The owned allocation remains32KiB. Payload `1000..6a00`; request `6a00..6a3c`;
request guard `6a3c..6a40`; result `6a40..74b8` (670dwords); guard `74b8..7500`;
IDT `7500..7d00`; stack `7d00..8000` (768bytes). Historical bridge commentary
says2KiB, but the actual offsets and independent bounds checks specify768bytes.
No larger physical allocation or relaxed ownership gate is used.

The13-row report displays the signature, return code, eight recovery masks and
CR09 before/after/restored. Twenty additional masks are aggregate-only: final801
requires all28 clear. A photo is native result evidence; preparation files alone
do not contain the post-handoff native results.

## Preserved failures

- Initial uncompressed code did not fit the payload reserve; measure001..004
  retain the size comparisons. There was no rejected-payload console launch.
- `host004`: ASan caught a stale13-entry host test array after14 relocations.
  Original sources are in `rejected-host004/`.
- `integration008`: independently configured native CPU exposed a broad identifier
  replacement that also changed the CPU mask. `model001/002`, `equivalence001`,
  `payload007` and `host005` are **invalid native qualification**. Their sources
  and evidence remain in `rejected-cpu001/` and qualification-failure002.
- `integration009`: the independent framebuffer oracle caught a512-byte pixel
  origin changed accidentally to768 during the stack-layout remap. `bridge003.S`
  restores only the pixel origin; `host006` is superseded. See failure003.

Large JSON execution receipts are retained losslessly in explicitly labeled
zlib/base64 text envelopes. `receipt-storage001.json` pins original and stored
hashes. Run `restore_receipts001.py` to verify or reconstruct the exact JSON;
it never overwrites existing receipts or executes a fixture. These contain our
numeric test traces, not proprietary software, screenshots or console memory.
