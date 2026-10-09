# Interpreting a Cancel request

A completed SendMessageTimeout call means the window processed the message within
the bound. It does not prove the wizard accepted cancellation or that the setup
queue drained. Both closed cancellation attempts deliberately retain the timeout
and blocked restart when the third wizard stays pending.

Microsoft documents that a property sheet page may reject cancellation or ask for
confirmation through [PSN_QUERYCANCEL](https://learn.microsoft.com/en-us/windows/win32/controls/psn-querycancel).
The documentation describes a possible mechanism, not evidence that the owned NT5
newdev page actually uses it. Its current minimum-version table is not proof of
Windows2000 behavior. Actual pinned binary imports, runtime page/control state,
owner identity, window closure and the genuine pending-install query remain the
validation evidence.

The new cancel003 diagnostic changes only the guardian failure path: after the
same helper002 joins with a nonzero exit, it launches the already reviewed188
read-only observer. Five bounded samples capture full command lines, top and child
window text/control IDs, pending-install queries and device/volume metadata. No
observer input or restart is requested. A complete inventory with cold integrity
can qualify this diagnostic even though cancellation and strict boot events remain
failed. It cannot qualify an unattended hardware trial.

The earlier cancel001 framebuffer snapshot paused/resumed xemu through HMP.
Its separate correction record marks that debugger observation. Cancel003 does
not use that capture path. Process IDs may be reused: cancellation action tuples
also retain process creation times, and inventory process IDs alone must not be
claimed to prove an old process lifetime.
