# Next: verify successful runtime dump extents

Both control001 and candidate001 are CLOSED, fully collected and verified.
Never relaunch/recollect them. Read REPORT.md,DESIGN.md,pair-review.json,
fatx-review.json and actual fixture/preflight/audit/closure records.
Candidate0103 strict bounded PASS; controlFALSE44+49. All same792/32/132/11
workload/cold integrity checks. No settings or event gates changed.

Use a NEW unique debugger child from the same prepared candidate inputs. Pin
FATX247246b61f6b2f6bee25423860b8b3800290e84e405186efa69785b1609213b3,
HAL7c6a3bfb9b6794c3b6fbce95fb76dc57d003843c19512b3ddb186604f668ed08,
and owned kernel84172dbd... Actual FATX entry/query RVAs are in fatx-review.json.
Adapt dump-fsctl-trace without reusing its attempts or frozen files. Its19-site
kernel review and paired frame/thread handling already capture usage, query,
FSCTL, pending branch and final caller. Stop at successful caller return.

At a successful FSCTL return, capture the four-byte output pointer and bounded
16-byte pairs until zero length. Validate positive lengths, sum=requestedbytes,
volume bounds, zero termination and actual code/resident pins. Inspect retained
DCB mapping pointer/length/request fields only with pinned consumer evidence;
do not assume successful setup from a stale IOSB or event absence. The previous
failure's IOSB remained the preceding query result while EAX held failure.

Independent cold oracle in cold-map.py: pagefile96MiB/1536clusters. First65536
bytes => length65536, volume-byte-offset140436013056, then zero pair. The
pagefile is beyond128GiB: preserve full64-bit arithmetic and later verify real
dump-miniport large-LBA behavior. Kernel dump context global and fields are
visible in dump-fsctl-trace/contract-review.json, but static leads need runtime
confirmation. Full breakpoint teardown, normal workload, cold audit and exact
frozen evidence remain required; debugger timing is not ordinary qualification.

Only after runtime map verification plan a controlled sacrificial dump and
recovery validation. No physical deployment, dump-policy/event suppression,
fake success or silent gate waiver. Original physical111 non-ASCII damage and
first restart remain unresolved. Preserve0101/video0093 physical,0088rollback,
immutable0.1.0 and inherited emulator-only null/unsupported-device policy.

ALL sessions CLOSED: hosttest21351,candidatebuild59319,controlbuild64382,
controlprep75665,runner8185,supervisor36300,audit28790,evidence58894;
candidateprep91309,runner24592,supervisor26870,audit36649,pairverification76446.
Other cold/configuration/closure/replay calls completed synchronously. No owned
guest/build/observer remains. Check time before work; cutoff13:00UTC October7.
At cutoff no new experiments, preserve/clean/report/pause automation. C: had
about21.8GB free before final reports; retain the20GiB build guard and inspect
actual capacity before any further build. No backing-chain relocation.
