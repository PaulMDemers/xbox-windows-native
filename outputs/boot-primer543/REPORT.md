# 543 closed: ordinary desktop and normal restart supported

One unchanged ordinary Windows launch accepted22:43:30UTC. User reported
"Windows is waiting at the desktop", then "It has rebooted and is at the dash"
in response to the explicit normal Windows Restart/no-powercycle request.
Fresh paired collection completed23:06:50UTC. All five hives pass independent
structure/raw-value checks. EventLog6005 and6006 deltas are each1. Ordinary
launcher, startup, application log and video trace remain byte-identical.

New events: Ftdisk49, EventLog6009/6005/6006, Tcpip4201 and Srv2013 for Windows F:.
Preserve the Ftdisk limitation and F: warning; this was not a full filesystem
allocation or free-space audit. No new Application Popup record in this run
does not resolve the previously observed shutdown popup issue.

No hook or remote file writes; all owned supervisors closed. No543 retry or
recollection permitted. This successful primer establishes the condition for
one final fresh warm544 checkpoint, not general boot reliability or a fix.
After544 closure, table boot investigation and return to combined3D545.
