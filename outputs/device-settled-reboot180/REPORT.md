# Host bootstrap failure; no Windows launch

180 preserved179's normally shut down disk and verified virtual equality after
a metadata-only copy/rebase. Preparation/full cold preflight/source freeze passed.
The rebase nevertheless stored an absolute Linux /mnt/c backing path. Windows
xemu refused opening that path and closed before the private monitor/link could
start. No supervisor ran, no SITE EXEC request and no Windows workload occurred.
runner host process exited; all owned sessions CLOSED. Never relaunch/recollect.

Actual xemu-stderr.log identifies the /mnt/c path. host-closure.json cold-compares
every prepared payload and all5hives to the captured parent, verifies full clean
323directories/6725files/324clusters0errors/orphans,44frozenpins/source snapshots.
Workload/strict/ordinary qualification remainFALSE. This is a host harness failure,
not a guest shutdown/PnP failure. No physical access, driver or configuration change.

Earlier readiness guard refusal also remains host-ready-refusal001.json: a Run
request before preparation finished was rejected before bootstrap. Nothing was
relaunched after a Windows request. Both failed observations remain preserved.

Fresh181 must use a verified same-directory relative basename for the copied
parent's backing path and inspect every stored backing filename for Windows
portability before bootstrap. Preserve180's original sources/disks/logs,179's
successful first configuration outcome and strict inheritedFtdisk49 failure.
