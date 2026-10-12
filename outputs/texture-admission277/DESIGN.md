# Texture observation while retaining dirty surfaces

277 is a host-tested proposal, not an installed renderer or release helper.
The four callbacks observed in276 have exact live renderer surface owners.
Two have native allocation matches; two unbound surfaces have unresolved native
allocation provenance. Their addresses are not evidence of firmware ownership.

The proposed operation only observes four already-owned standalone texture
objects. It neither reads the dirty surfaces' guest bytes nor changes their
objects, callbacks or lifetime. Unbound surfaces can therefore remain outside
the texture operation if complete current renderer ownership and disjointness
are proved. This is a scope decision, not proof that their native allocations
belong to the test or permission to retire the backend. A future whole-backend
handoff still needs guest allocation provenance, scanout and all other owners.

The new opt-in contract must carry the four actual4096-byte physical allocations
from an independently attested271 checkpoint. The actual locked texture cache
must independently match each source at allocation+256,512 bytes, no palette,
one cache edge, one unit edge and two references. Protect the full allocations,
including guards, against every retained surface, not only the source pixels.
No release is authorized by this contract; release_requested explicitly fails.

## Two complete boundaries per transaction

The runtime adapter must retain stopped guest CPUs, closed frontend, halted
PFIFO publication, an actual owner worker, finite render/display fences, native
context identities and complete pending/GET/PUT/method checks. The scalar core
cannot establish those facts; caller booleans alone are not runtime evidence.

An actual CPU-exclusive queued job captures the complete callback list after
earlier queued jobs. Under renderer/PGRAPH locks, copy the complete surface
graph. Require a one-to-one callback/surface correspondence with exact callback
identity, range, function, MemoryRegion, opaque device and absolute RAM address.
The existing CPU-owned function/region/device classifier remains mandatory.
Unknown callbacks, missing/duplicate edges, excess capacity, invalid bounds,
multiple claimed current color/depth bindings or any download/upload/eviction
pending flag refuse. draw_dirty may remain set; it must not be cleared.

Collect a second acknowledged CPU inventory and a second locked surface graph.
Require complete tuples and graph fields unchanged within this transaction.
Do not follow any saved callback pointer; only the live CPU list is dereferenced
on its owning CPU and only live renderer objects under their owning locks.
Actual source/kernel/physical allocation attestations remain the standalone
controller's responsibility. Windows258 attestation is not a substitute.

Pointer equality is insufficient for ABA. Proposed clock.c instruments the
actual CPU list insertion and unlink bodies after their original queue mutation.
A saturating64-bit global clock advances for each completed mutation. The first
CPU becomes its owner; any other CPU or nonexclusive/wrong-thread invocation
sets a sticky error. The original list mutation/free still executes unchanged;
this diagnostic never inhibits normal callback work. There is no reset API.
The owning exclusive audit copies clock and sticky error before publishing its
acknowledgment. Both checkpoints must have the same nonzero nonsaturated clock.
Remove/reinsert at the same pointer/range therefore refuses even when the final
list is byte-identical. The global scope deliberately refuses foreign-CPU work.

Exact source confirms async_safe_run_on_cpu queues an exclusive job; the work
item is removed before execution and executes between start_exclusive and
end_exclusive outside the BQL. Empty queue observation alone remains invalid.
Clock equality is not protection against uninstrumented mutation: the source
closure must prove every actual insertion/unlink goes through these two bodies.
GL and Vulkan registration paths call the same API; only the known GL callback
classifier can qualify this texture observation. No renderer switch is allowed.

For a new runtime adapter, move observer arming for the opt-in mode until after
both CPU inventories, complete graph validation and a final locked recheck.
Do not allow its old zero-count branch to arm before the new proof. The original
capture,1 and observe276 behavior stays unchanged. End capture similarly must
validate the new proof explicitly rather than zeroing counts for x274_admit.
Clocks may legitimately differ between the initial and final transactions after
normal guest rendering; each transaction must independently be stable. Actual
texture generation/key/source/RGBA reuse still needs273's bounded observer and
independent pixel oracle. Terminal transport must expose the full clock/tuple
evidence, union all errors and require acknowledged sealing.

## Host evidence and limits

host002 runs the proposed pure admission core and exact original insert/unlink
bodies with only the metadata calls inserted. QEMU queue macros are pinned and
real; CPU scheduling, exclusive identity and trace APIs are explicit models.
Real pthread release/acquire publication is tested. The real276 surface tuples,
texture identities and ranges seed a model fixture; missing second acknowledgment,
clock and context admission fields are explicitly synthetic.276 still refuses.

20,771 checks pass under ASan/UBSan, including4096 actual queue insertion/unlink/
free pairs and1024 publication races. Negative cases cover same-pointer ABA,
saturation, foreign/nonexclusive CPU, unknown function/region/device, missing or
duplicated edges, invalid or wrapping ranges, guard-only overlap, changing dirty
state, invalid context/epoch/acknowledgment and attempted release. Host001's
20,762 passing checks and exact inputs remain preserved;002 additionally rejects
nonboolean gate values and duplicate color/depth role claims.

No real queued CPU acknowledgment, renderer fence, GL pixel result, guest reuse,
disposal, native GPU ownership or performance improvement is established here.
No shared xemu, native, SDK or physical file was changed by these tests.
