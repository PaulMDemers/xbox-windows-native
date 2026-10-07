# Namespace/file lock ordering candidate0100

The driver built and passed checksum/import review. Its initial three-worker
fixture001 was prepared but NEVER launched: it inherited the discovered wait-all
harness bug and is explicitly held by fixture-hold.json/Run.ps1. The corrected
[five-worker stress](../fatx-namespace-stress/README.md) is the next runtime test.

This extends the cleanup-only0099 causal candidate. The exact0098 control
snapshot proved a cleanup/volume-flush exclusive lock cycle. The static review
also found reverse-order waits in overwrite-create, directory enumeration and
selected set-information operations. This candidate addresses those ordinary
file paths; volume lock/dismount and arbitrary concurrent mapped truncation
remain separate validation work. It is not physically qualified.

Enumeration and metadata updates use the FILE_OBJECT's live FCB reference to
take MainResource before DirResource. Nonblocking acquisition failures release
any acquired resource before the existing queue/buffer-pinning path. Normal and
allocation-failure exits release DirResource before MainResource.

An overwrite starts with namespace lookup, so it cannot simply take an old file
lock and proceed after dropping the namespace lock. It tries MainResource
without waiting while DirResource is held. On contention it pins the target,
closes the incomplete file-object attachment, drops DirResource, waits for and
releases MainResource, then releases its extra FCB reference under DirResource.
It repeats the full pathname/share validation before any mutation. The pinned
object is never used as the overwrite target after a rename/delete opportunity.
The three validation exits after successful acquisition release MainResource
before closing the file attachment. Volume and open-target-directory paths keep
their existing behavior.

The first validation uses exactly the reviewed three-worker500-iteration
concurrency executable from the unchanged-driver control. Only the driver
differs in a fresh sibling fixture. Preserve every run and its cold audit;
compilation, a desktop or a dashboard return alone is not qualification.
