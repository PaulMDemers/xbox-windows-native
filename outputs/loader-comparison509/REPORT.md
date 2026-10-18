# 509 static comparison complete; physical cause still unknown

Six retained XBE images passed the new parser's bounded structural checks. Five build images match their actual staged hashes and cold physical copies; the sixth is the ordinary launcher captured before508. All original inputs remain unchanged. The parser rejects993 targeted structural, digest and truncation mutations. This establishes the stated static invariants, not complete XBE validity, signature acceptance, current physical mappings or kernel-call behavior.

| Image / physical attempt | File bytes | Header entry | Page-rounded image end | Recorded result |
| --- | ---: | --- | --- | --- |
| 483 | 541526 | 0x11100 | 0x95000 | Windows sample and normal restart |
| 487 | 541526 | 0x11100 | 0x95000 | Preparation/witness; no Windows result |
| 494 | 542839 | 0x11100 | 0x95000 | Windows sample and normal restart |
| 499 / 501 | 545004 | 0x94877 | 0x96000 | Entry receipt absent |
| 504 / 508 | 545088 | 0x94aff | 0x96000 | Entry receipt absent; LED unknown |
| Ordinary launcher captured before508 | 300624 | 0x11100 | 0x5a000 | No launch in this comparison |

Relative to494, the only different header DWORDs in499/504 are image size and encoded entry. Section size/digest and contents also differ; this is not an otherwise identical A/B comparison. Certificate, media/region, stack/heap fields and TLS-pointer bytes are common across all six. Added ordinals50/99 in504 exist in the historical307 physical kernel export record and match the pinned nxdk definitions. That proves neither today's physical import resolution nor successful calls. The earlier507 emulator used a different kernel image identity.

Successful494's validated context path includes capture code at0x9473e..0x94877 on the same0x94000 page as504's entry. Therefore a blanket claim that this code page cannot execute physically is unsupported. The new entry state/data starts at0x95000, an additional page relative to494. Direct entry at the higher address and the added data page remain separate untested variables. Low entry alone is not sufficient:487 failed later despite using0x11100.

The inherited TLS pointer0x18000 points into identical payload bytes in every image. Interpreting those bytes using the generic TLS structure fails an in-image range sanity check, including in successful images. Runtime handling remains unknown; it is not a new regression or an established explanation, and no TLS patch was made.

Review001's mistaken487 stage filename caused FileNotFoundError; source and failure are preserved. Review002 corrects only that filename/output ID. No build, emulator, physical access, startup hook, SDK/shared-source change or launch occurred. The508 result stays closed and unresolved. The pending user LED observation may refine it without rerunning the test.
