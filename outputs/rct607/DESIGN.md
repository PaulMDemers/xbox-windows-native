# Qualify observed missing CreateDIBSection output pointer

606's internal GDI call returned a bitmap with NULL ppvBits. The observer wrongly
required that address to be readable and terminated the game. Keep606 failed.
Change only the diagnostic handling of a NULL output address for CreateDIBSection:
emit OUTPUT_ABSENT with the call/API/zero address and preserve its return value.
Do not read NULL or invent a bits pointer. Keep non-NULL read failures fatal;
DirectDraw output/interface requirements stay unchanged.

A fresh original NT5 control preserves605's graphics/header/phase tests, then
creates RGB and BI_BITFIELDS8x8 bitmaps with NULL output addresses, inspects their
DIBSECTION objects through GetObjectA and deletes them. An invalid header with
NULL output must fail without crashing. Both pristine/traced subject logs must
match. The header reader still marks BI_BITFIELDS unsupported; masks are not read.

The independent parser accepts an absent-output record only for a paired
CreateDIBSection return whose recorded output address is exactly NULL. Reject
false API, false/non-NULL address, missing/duplicate records and fabricated output
pointers. No blanket output/read waiver or game/driver modification. Normal
restart and cold checks required before any new game retry.
