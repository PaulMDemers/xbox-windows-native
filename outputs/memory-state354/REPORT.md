# Read-only memory-state354

The private RosBE diagnostic compiled and passed import/residency/privileged-write review. Actual collector host tests passed2524 checks; independent decoder tests16406. CPU, GDI and page interfaces were modeled in host tests. No physical access or cache writes.

Actual355 first packet refused a nonpresent shadow PTE. Nine later complete packets were incorrectly rejected by decoder354's assumption that the opaque HSURF must be a kernel pointer. The original decoder and failed audit remain unchanged. Separate357 analysis corrects that host decoder error only: nine complete emulator samples resolve shadow WB and scanout UC; the first incomplete packet still fails. This is not evidence of physical cache state or a timing cause.

Installed source review distinguishes actual300 bootvid/miniport reservation and303 display from unrelated old provider source in351. The visible scanout uses the55MiB reserved physical range, not historical0094 GPU mapping. API cache intent alone is insufficient.

Reviewer001 forwarded-RtlUnwind and002 warning-classification refusals preserved;003 checks the actual NT kernel forward target and inherited warnings. No new warning messages. See build001, binary-review003, source-review001 and host001.
