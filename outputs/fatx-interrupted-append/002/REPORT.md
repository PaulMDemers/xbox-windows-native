# Later checkpoint missed because host trace publication failed

Emulator-only launch06:14:53UTC7October2026. The tracer hit a Windows
PermissionError replacing trace.json and entered cleanup at06:16:43UTC. It
removed all breakpoints, left no pending log writes and resumed the guest.
Its final atomic replacement also failed, leaving the complete final JSON in
trace.tmp. The last published JSON therefore appeared to remain active.

After collecting the tracer's exit1, both original records were preserved as
trace-last-published.json and trace-final-recovered.json. The exact final record
was republished to the existing observer; no guest was relaunched. The observer
then signalled owned cleanup, completed06:19:48UTC. All sessions closed.

This attempt did NOT reach the selected1524-byte checkpoint and supplies no
controlled-interruption conclusion. The final cold file contains the full220
warning correctly, allocation is consistent with no orphans, five hives parse,
and one normal EventLog shutdown record exists. Those results do not turn the
failed tracing intervention into a successful diagnostic or ordinary qualifier.

A recorder fix now retries PermissionError for a bounded3seconds while retaining
atomic replacement. A real Windows test held a reader handle without delete
sharing: transient contention succeeded after release; permanent contention
preserved both old JSON and complete new temporary JSON. The test is recorded
in atomic-json-test.json. This validates recovery from a plausible sharing
collision; it does not independently establish which reader held the failed
attempt's file handle. The exact002 source and all failed evidence are retained.

Case003 is a fresh overlay using the same1524-byte checkpoint and corrected
host recorder. No guest, driver or physical-console modification is involved.
