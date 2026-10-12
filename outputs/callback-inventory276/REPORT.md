#276 closed: all four refused CPU callbacks identified

Scoped refusal-inventory observation PASS. Admission and strict qualification
remain FALSE. One standalone launch01:00:01UTC closed01:00:30UTC, October12.
No texture observer arm, guest reuse draw, callback removal, release, native
driver/SDK/physical change or native GPU grant.

The actual CPU-exclusive epoch1 recorded four callbacks. Each matches exactly
one live SurfaceBinding identity, offset and size. All use the same captured
function/region/device identities and passed the original CPU ownership
classifier. All four surfaces have draw_dirty=1, no other pending flags:

| VRAM offset | Bytes | GL name | Current role | Native allocation match |
|---:|---:|---:|---|---|
|54329344|2457600|12|Unbound|Not in captured native ranges|
|53100544|1228800|15|Unbound|Not in captured native ranges|
|60276736|1228800|14|Depth|Exact current depth buffer|
|59047936|1228800|21|Color|Exact extra target|

None overlaps the four owned texture allocations. These are actual addresses
for this run only. The two unbound surfaces' native allocation provenance is
unresolved; known renderer ownership does not prove guest allocation ownership.
No second CPU acknowledgment, stable callback lifetime or retirement follows.

Complete graph55624rows/218pages and UI8pages preserved,48 original shader work
functions returned (not thread exit/join).264 indexed binding rows/305 known
container attachments, actual render/display/UI contexts65538/65539/65537 in
this run.34 native captures and raw private HMP replies rehashed. Twelve actual
callback/owner/range mutations rejected. Native phase11 had exact720 framebuffer,
16384 source/guard and384 vertex bytes, and all15 object descriptors as in275.

The new getter reads acknowledged saved metadata, never dereferences saved
callback pointers. Bounded65536-byte response and capacity256. The observe276
request preserves reason14 and terminates with reason27 even if count becomes
zero, before arming any texture observer. Source inversion reconstructed the
entire original renderer after removing only the recorded additions. Actual
getter host tests17688checks/1024 publication races,30 independent wire
mutations;4128 actual no-arm branch cases. ASan/UBSan clean. Windows sharing
tests cover transient retry and permanent-lock preservation. Runtime collected
all pages without the275 writer failure. A separate status reader briefly hit
a sharing denial; it did not affect the controller or qualification.

Reviewed build0037a19d5c3...191777779bytes,79 inherited warnings/no new messages,
19 borrowed sources restored. Build001 failed missing public declaration;
build002 compiled but review rejected a new printf-format warning. Both are
preserved and never launched. Build003 adds the compiler format annotation;
its exact getter was retested. Host002 source-review attempt passed branch
tests but then rejected that warning; corrected review used fresh host004.

Guest quarantined at initial refusal. Frontend reopened once, breakpoints
removed, physical mode restored, orderly host exit0/no fallback. No normal
guest terminal or Windows restart claim. QCOW structures and EEPROM clean;
full8GiB disk equality still FALSE for the same one reserved-sector1536 byte.
Complete map/65536 overlay comparison proves filesystem bytes inherited
unchanged, with no writer attribution or waiver. No ordinary/performance,
whole-backend retirement, native Windows ownership or hardware promotion.

Closed185 non-backing portable was hash-verified onE with original junction,
portable-276.json. No backing chains moved. All276 runtime and failure records
are closed; never relaunch/recollect/parent this disk.
