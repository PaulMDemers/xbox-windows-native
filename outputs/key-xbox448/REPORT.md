# Physical RGB32 key probe prepared; not deployed

The package is built and statically verified. It contains the exact keyprobe
binary qualified in447 and a new physical controller derived from the actual446
controller by fixture/schema/source-copy path changes only. There is no desktop
mode-switch code. Controller/probe imports match24/23 actual NT5 exports.

The package source, executable hashes and host dependencies are recorded in
package001.json. Payloads are private under work/key-xbox448/payload. No Windows
binaries, hives or captures are included in the public repository.

The read-only dashboard connection attempt timed out while connecting to FTP,
before authentication or baseline verification. No upload, startup hook, launch
request or Xbox filesystem change occurred. This is an availability observation,
not a boot or graphics failure. The user was asked to leave the console at UnleashX.

Once reachable, stage with fresh owned E: paths and readback, verify the unchanged
720p/32-bit baseline and runtime, issue one launch, observe the bounded normal
restart, disable the hook first, then collect and independently validate results.
No physical qualification exists for this package yet. Earlier physical442 and
historical system issues remain separate.
