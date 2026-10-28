# Failures

Photo decode001 failed: component threshold65 found31 of32 cells in row11.
The original photo, decoder and failed photo001 receipt are retained. Read-only
pixel inspection showed reflected dark cells. Decoder002 uses component cutoff100;
all416 bits agree at five offsets and three classification thresholds, plus352
adjacent-row checks. Maximum black median channel85; minimum white mean203.67.
No expected value was substituted. Native hardware result is green with zero
cleanup masks. No749 launch/recovery failure observed; collection and audit passed; runtime closed.
Earlier failures remain in closed kits.

Closeout read-only lookups for audit001.py and audit.py failed (files absent).
Discovered and reused audit_collection.py source; no runtime/collection affected.
