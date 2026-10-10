# Completed-copy accounting119 builds210

Both matched fresh builds compiled from source tree
`c8654947539246de3ce1e386e7007e124fcaa98f`. Only XWN_UPLOAD_ACCOUNTING differs;
XWN_TEXT_BOUNDS ON, XWN_UC_STORES and XWN_BODY_PROFILE OFF both. Existing Eng
render calls, upload geometry/clip enumeration, cache and ownership are unchanged.

OFF DLL SHA256 db79d42929ea155b9ac1dcc240dace7fd1e6f136723a83484f5221185119a715;
ON7c3901dd3e457f6cdeb4e4c0e2fb82d2fd6ae1ec9a489cc7be2fe4bd35afba31.
Actual provider imports match, no new import. Compiled resident instruction review
proves OFF publication is a stub, ON has protected writes/calls; no vector/FPU
instruction in the reviewed publication/snapshot bodies. File size is not a
feature-presence test; actual runtime packet mode/coverage is required.

Accounting is local during copying and published once after copy under the
existing ownership semaphore. It never holds that semaphore over rendering or
framebuffer IO and never uses a mutable current-kind tag. Explicit kinds cover
fourteen DDIs and both surface-lifecycle callers. Fixed read-only632-byte119
packets expose saturating requests, explicit/null counts, boxes, bytes, NULL-input
bytes and clip fallback counts. Overflow/error/reserved fields fail closed.
NULL-input bytes are not a claim of unnecessary transfer.

Host-only ASan/UBSan tests pass127,131 checks for OFF and188,580 for ON, including
independent seeded accounting and32/64-bit boundary saturation. These tests do
not simulate GDI rendering or establish physical behavior. First direct build
lease refusal was preserved before any source/output creation; subsequent owned
wait-build attempt1 compiled normally. Root build session72692 is CLOSED.

Fresh211 v12 runtime owns actual pixel/phase/cold and later physical evidence.
Original physical0101/video0093,0088 rollback and immutable0.1.0 are unchanged.
No speed fix, baseline promotion, cache change or new-mode qualification is
established by these source, arithmetic and compilation reviews.
