# 690 kernel reference and framebuffer check — closed

The user confirmed the white border, blue header and red/green/blue/white panels
worked, followed by automatic dashboard return. All six exclusive reports were
collected twice with matching bytes. The final report records restart requested;
this was a kernel application, not a Windows shutdown or native boot test.

## Actual console evidence

On the incoming user-identified 1.6 (kernel 1.0.5838.1, GPU d3/MCP d5, 64 MiB),
kernel PCI reads report SMBus ID `01b410de`, command/status `00b00001`, BAR1 `c001`.
Kernel byte reads all succeeded: cable1, EEPROM standard `00400100`, video flags
`0e`, encoder address E0/register0 value4. These match689's PCI/cable/configuration
expectations **in kernel context**. They do not prove the same state existed at
689's early native entry, reveal its failure phase, or validate its four-byte
native encoder transaction. The encoder byte is not a unique chip identifier.

The SDK allocated 3,686,400 bytes for1280x720x32 with pitch5120. Its physical span
was `[03c5c000,03fe0000)`, matching scanout. All900 page translations and the last
byte matched contiguous arithmetic; allocation size matched. Every pixel was
written within that admitted allocation. The span does not overlap the planning
ranges for GDT, IDT clear, firmware/BSS and stack. This is one allocation under
the live kernel, not proof it survives a handoff or a reservation for future runs.
Never hard-code the observed address into a native image.

## Validation and limits

Fresh nxdk build uses SDK58427c078b4ccb0121f359b6b6c536b3b2914976. Sanitizer tests
cover layout bounds, reservation edges and all921600 pattern pixels.38 cases run
the actual32-bit layout object under Unicorn with an explicit harness memcpy
helper; kernel services and physical mappings are not modeled by those cases.
The first object review failed before fixture execution because its loader did
not resolve the compiler's memcpy dependency. Both harness versions and failure
receipt are retained. The original build warning about an already merged section
is retained in the private build log.

One SITE launch was accepted at00:28:42 UTC on October27. First collection at
00:29:05 was refused at connection, with no files read. After the user confirmed
return, collection002 retrieved all six phases. This was one physical launch,
not a rerun. Stage ownership/executable bytes and unrelated E/application entries
matched. Directory comparison is not a whole-volume FATX health audit. No startup
hook, console C access, native handoff, ordinary launcher change, Windows test or
encoder-register transplant occurred. SDK mode setup used normal kernel services;
these and kernel SMBus calls do not have application-enforced timeouts.

All invoked host fixtures and this physical runtime are CLOSED. No host process
or build lease remains. The owned E directory and reports are retained, hardware
ticket retained, automation paused. Incoming1.6 is at UnleashX with HDMI. Do not
rerun or recollect this closed runtime. No native driver support is promoted.

Evidence: [build](build001.json), [sanitizers](host001.json),
[failed object harness](object-review001.json), [corrected cases](object-review002.json),
[review](review001.json), [stage](stage001.json), [launch](launch001.json),
[connection failure](collection001.json), [collection](collection002.json),
[user observation](observation001.json), [analysis](analysis001.json),
[closure](closure001.json), [next work](NEXT.md).
