# 673: receiver readiness failure isolated on the host

672's single accepted physical launch has no usable UDP capture. Its receiver
bound port50657 and published readiness, then exited1 because the fresh
configuration used `signal672physical001` as its fixture. The unchanged655
receiver accepts only `physical-candidate` or `host-loopback`. This was an
operator/harness configuration error, not evidence of zero network traffic.
The readiness race allowed console launch after the receiver had died while
the controller performed slow FTP verification. Preserve672 unchanged.

readiness.py is a HOST-ONLY replacement contract for a future controller:
validate the manifest, fixture, exact candidate identity, port and duration
before opening a socket or publishing readiness. Publish the verified identity
and owned PID after binding. After all slow stage reads and immediately before
persisting the one-shot SITE request, call admit_live_receiver with the actual
owned Popen object. It rejects missing validation, wrong identity/PID and an
already-exited child. The child can still die after the last poll: that remains
a failed capture, never permission to repeat an accepted/uncertain launch.

test001 passes21 checks using fake sockets and process states. It reproduces
the actual672 bad configuration, verifies rejection before any socket/readiness,
checks malformed identity/port/bounds, bind failure/closure, valid modeled
capture, stale/forged readiness, used paths and child death during staging.
The original private672 configuration remains byte-identical. No real sockets,
console contact, launch, collection, fixture boot or firmware change occurred.

This helper is not retroactively applied to672's frozen scripts. A future
fresh physical controller must integrate receive() in its listener and make
admit_live_receiver() mandatory at its final SITE boundary, then exercise the
complete controller with accepted/uncertain requests and a child exit during
slow staging. Do not call the failed672 listener again or relaunch672.

No firewall relaxation, admission waiver or claim of physical UDP delivery.
All error receipts and earlier closed attempts are retained.
