# Native NVVVALIDSTART checkpoint779

Source-only continuation from closed777 frontend and closed778 kernel probe.
The custom probe adds the pinned source-order zero write to680814 and recovery
to its own saved zero, after NVVCRTC479 and before reverse recovery. Eight
neighbor triples are checked. Same-value dropped forward/undo stores cannot
be distinguished by unchanged readback; wrong-write-plus-dropped-undo is tested.

This is an intentional native hold, not a full mode switch or Windows1.6 boot.
The SDK prepares720p before the native handoff. No later vertical sync/end,
encoder/clock/scanout programming or CR1b/CR22/CR33 writes are added.

## Evidence and boundaries

Fresh native payload, independently constructed pages,419 direct ELF cases,
relocated bridge/integration faults, exact optical pixels and diskless CPU
fixtures are required before a linked nxdk build is admitted. These host models
prove access/control flow and memory boundaries, not physical GPU semantics.
The payload occupies1000..4700, IDT4800..5000,340word result5100..5650,
guard5650..6000 and reserved stack6000..8000. Four layouts are verified.

The13optical rows expose signature, final code, seven cleanup masks, zero
target and before/after/restored values. Ten additional masks are aggregate-only
through final success, which requires all17clear. Neighbor/CPU/selector details
are not individually shown. Decode the actual photo against optical-schema001;
never infer success solely from color or preparation JSON.

Use physical003.py for exact uniqueE stage/readback and single SITE launch with
20-second reply bound. No hook is installed. After the photo is captured, request
manual power-cycle, then collect preparation files once with double readback.
Those records stop at handoff_armed; they cannot replace the native photo and
manual reset cannot prove normal Windows shutdown. See NEXT.md for actual state.
