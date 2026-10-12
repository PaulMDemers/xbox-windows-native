# 292 physical standalone HD mode control

One physical launch at 17:33:44 UTC on October 12 selected 720p, 1920x1080, then 640x480 using the stock Xbox kernel mode API and returned to UnleashX. Independent CRCs match all 13,209,600 framebuffer bytes; native byte comparison reported zero mismatches. The 1080 buffer is 8,294,400 bytes. Visible TV stability remains pending the user's observation; memory readback alone cannot prove field timing or display lock.

| Mode | Bytes | CRC32 |
|---|---:|---|
| 1280x720 | 3686400 | dfa8cb56 |
| 1920x1080 | 8294400 | 93b2b68c |
| 640x480 | 1228800 | fe495f63 |

The protected Windows payloads, normal startup and five hives are byte-identical before/after. No Windows driver or launcher changed. This is standalone hardware mode evidence, not Windows HD qualification. Fallback 640-wide memory has HVALID719, retaining the pitch-versus-timing distinction.

The same build003 binary first completed one fresh emulator control with actual XBE/text/caller attestation, all translated framebuffer pages, exact independent full-buffer comparison and native CRC agreement. Breakpoints were removed, physical mode restored and host exit was orderly. The original strict disk result remains FALSE: one reserved-sector byte changed. Complete 8 GiB map/65536 overlay-byte review proves filesystem bytes inherited unchanged; QCOW structure and EEPROM match. No historical gate is waived.

Build001 failed C string/path escaping; build002 compiled but failed warning review on a transient make clock-skew warning. Both inputs/logs remain. Build003 adds a two-second copy timestamp settling interval; warning policy is unchanged. Nine decoder negative cases reject malformed results. All frozen dependencies and private captures rehashed in final-review.json.

Two inherited cosmetic helper descriptions remain frozen: prepare prints 289 and a physical helper comment says inventory-only. The actual 292 native code, mode_changes=true record and three mode logs establish the executed behavior. No frozen input was edited to correct prose.

No repeat launch or recollection is needed. All owned processes are closed. Private build/runtime files remain E:/xwn292; native executable SHA256 cb884d1a81c6b6c6d0cce0ef0213e04a59d3826e5c950ed6efa45039d6245194.
