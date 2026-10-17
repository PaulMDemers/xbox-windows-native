# Xbox RGB32 diagnostic: accepted launch without a result

The prepared package was verified against all 21 frozen dependencies and both
payload hashes. Dashboard authentication, the existing 720p baseline, protected
runtime files and normal startup passed. Staging and readback completed.

One FTP launch was accepted at 2026-10-17 19:28:05 UTC. The first observer
connection timed out; dashboard FTP was reachable at the next check, approximately
15 seconds after observation began. Repeated checks found no runner receipt.
Collection confirmed that no xwn448 result directory existed. This does not
identify whether the loader or Windows was reached; visual observation remains
pending. No sample execution or normal Windows restart is proved.

The temporary startup hook was disabled first and preserved as
E:/xwn448-kit/startup-used.cmd. The original launcher, normal startup, protected
code and 720p configuration verified unchanged. All five before/after registry
hives and both event logs are byte-identical. The five hives also passed clean
header and independent raw-value checks. Seventeen private before/after files,
21 frozen dependencies and both payloads were rehashed. Dashboard C was untouched.

The read-only observer was explicitly stopped after collection and the no-receipt
review. Its original partial record is retained unchanged, including closed=false;
observer-stop001.json records the exact owned process, reason, termination and
final observation hash. This is not a completed 480-second deadline observation.
All owned processes are closed. The prepared success-review scripts were not run:
they require sample receipts that do not exist. no-receipt-review001.json is the
separate review for this outcome.

The scoped hardware diagnostic remains unqualified; the earlier PC 24-bit result
is unchanged. No driver, DLL, display mode or boot-path change was made. Historical
Ftdisk49, shutdown popups and incomplete full-filesystem audit remain separate.
Never rerun or overwrite physical001. The retained package and disabled hook are
inert; any future physical attempt needs a fresh namespace and a reviewed launch
path. The earlier connection001 timeout is retained as a distinct pre-staging event.
