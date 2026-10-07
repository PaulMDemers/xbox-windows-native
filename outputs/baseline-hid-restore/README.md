# Restore an evidenced missing component in fresh emulator children

The unchanged settled parent configures automatic HidServ startup but lacks its
executable. ../baseline-event-forensics identifies the exact SCM error and both
matching preserved recovery copies. This kit restores only that19,728-byte
hidserv.exe (SHA256031a1fb5ca4194284d6ecfbfe8afe63589700c1376873267f131ead06946dc6a),
plus unique test helper/mode/startup payloads, in fresh owned overlays. No registry,
kernel, FATX, video, bootloader or device-policy change. Protected hashes include
the service's seven imported DLLs; all initial hives are unchanged.

The mapped-shrink/rendezvous workload is retained from ../fatx-map-rendezvous,
with read-only SCM status queries added after initial install-idle and after the
end idle. SERVICE_RUNNING=4 and both exit codes0 are required at each checkpoint;
START_PENDING can wait at most10seconds. The test does not start/stop/reconfigure
the service manually. Fresh serial control precedes the concurrent comparison.

Both require792 cycles,32 queried allocation shrinks,132 reopens,11 exact cold
files, full allocation/hives/protected hashes, normal restart and actual dashboard
return. Concurrent mode also requires44 dirty-map rendezvous with positive
append/dirty coverage per file-round. All prior limitations of the rendezvous
schedule and failure cleanup bounds apply. Source/fixture/28 parents are pinned.
The oracle additionally rejects stopped/failed-late service states (13 negatives).

Event gates are unchanged: eliminating SCM7000 cannot waive Ftdisk49 or any
other new warning/error. No service disable, event suppression, dialog cancellation
or physical deployment. This restores an owned component in the emulator; it
does not claim a physical change or solve the original byte corruption.
