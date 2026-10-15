# 403 validation boundaries

Use public anonymous source/archive pins for acquisition and fresh output roots.
Keep the historical compiler comparison separate from locally bootstrapped tool
receipts and newly compiled binaries. A receipt covers libraries and symlinks as
well as the compiler but is not an authenticity signature.

The public restore surface is deliberately offline standard-E raw-image work.
It does not format disks, access devices or connect to a console. Validate all
compressed and decompressed bytes before the writable image open; require both
outside-E hashes, preserve a write-started receipt, and verify all regions after
fsync. Failed attempts remain distinct; an intentional retry requires a fresh
receipt. Do not equate mountable metadata with exact payload preservation.

The disposable runtime uses the restored prepared baseline, then a separately
recorded helper/startup instrumentation step. Original archive, unused fixture,
restored image, boot copy and executed runtime remain distinct. Never parent a
new experiment from the executed disk. Original incorrect analysis records stay
immutable; corrections pin the raw evidence and state the changed interpretation.

The review export uses an explicit source/tool/current-guide allowlist, exact
entry hashes and deterministic ZIP metadata. No history, historical engineering
docs, private payloads or executable binaries enter it. Public release and final
license review remain separate from archive assembly.
