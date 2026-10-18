# Xbox windowed D3D presentation: scoped pass

One physical Xbox run completed both default and explicit HEL cases at
1280x720, 32-bit RGB. The unchanged sample from the491 Windows2000 PC control
passed all four stages: visible, covered, moved while covered, and uncovered.
The independent checker validated4,063,232 source/post-blit/GDI image bytes,
actual clip unions (1/4/4/1 rectangles), triangle vertices, render states and
unchanged source surfaces. The PC control used640x480 RGB565; these native
formats are recorded separately. This is the D3D7 RGB software renderer.

The only launch request was accepted at2026-10-18 06:27:32UTC. Dashboard return
was observed at06:29:25UTC. Both processes exited0, the bounded runner requested
restart, and EventLog6006 increased by one. The temporary startup hook was
removed before collection. The ordinary launcher, startup and protected720p
configuration were preserved. Xbox dashboardC was never accessed.

Strict system qualification remains FALSE: this run added Ftdisk49 and three
Application Popup26 records for rundll32.exe DLL initialization during window-
station shutdown. These are preserved in full cold event records. There were
no new Application-log records. Successful graphics and normal restart do not
resolve intermittent boot failures or shutdown-time device setup.

## What changed

The private launcher is exact490 code with four same-length ASCII log path
literals changed to XWNBoot492a and its XBE section SHA1 recomputed. Compilation
and an independent byte comparison found exactly24 differing bytes: four path
digits and20 checksum bytes. All other bytes, the original1024-byte loader,
payload,313-byte CPU capture, symbol addresses and diagnostic schema/cookie490
remain unchanged. Attempt492 is separately identified by unique paths and hash.

- XBE542,839bytes:7675ad0072345af1ddb6c98b5f4dc09142031e8607ed664f663f96726a40230d.
- Runner12,958bytes:b5a25504888b8ac6c1f29862df5adbbbcf615b3f8d3d28bf612e03dacab6072b.
- Unchanged actual491 sample31,294bytes:5bc04570fe39a6d68aae82ed24182ec280645594294967db3898d14e9f2d0a79.

The runner changes only the491 namespace and source-copy path. Compiler/header
pins are retained; both build logs are empty. All24 runner and50 sample static
imports matched owned NT5 exports. Seventeen actual dispatcher cases passed
with explicit FTP/baseline models, including no-repeat launch, hook-first
collection, incomplete context, directory capacity and bounded read retries.
There was no driver, paging, interrupt-state or video-mode change.

## Evidence and limits

The initial/witness/context records decode independently. Both actual register
snapshots match within this run;2577 mutated context records are rejected.
The kernel physical allocation was0x01f00000 and loader0x02000000 in this run;
these are observations, not prescribed addresses. No mapping/page-walk, cache
attribute, atomic snapshot or final paging-transition proof is inferred.

The graphics checker rejects1804 mutations of copies of the actual metadata
and pixels. Original files remain unchanged. The32-bit Xbox and16-bit PC use
the same predeclared oracle, with no expected-pixel adjustment. Private binaries,
Windows data and captured images remain outside the public repository.

See physical-final001.json, runtime-review001.json, actual-controls001.json,
actual-context001.json, module-review001.json and the frozen package/source
records for exact closure and provenance. No full FATX allocation audit was
performed in492. Native GPU acceleration, game compatibility, performance,
physical scanout and repeated boot stability remain unqualified. User visual
confirmation is separate from the machine-checked image result.
