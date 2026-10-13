# Console partition policy and read-only dashboard inventory

The user directs that Xbox dashboard C: be left alone. Do not write, delete,
move, clean or reformat files on it. In native Windows this partition is F:,
at byte offset2359820288. It is the target of the Srv2013 capacity warning in
physical331. This warning remains recorded; do not suppress it or rewrite the
failed qualification result. Softmod dashboard virtualization is not fully
established by the native offset alone.

Dashboard E: is the intended stock-drive installation target; dashboard F: may
be used on expanded disks. Stock 10 GB drive support is a goal, not a verified
result of the current installation. Native Windows currently maps dashboard
E: to D:, and dashboard F: to C:. Use physical partition identity, not an
assumed equal drive letter, in all packaging and deployment changes.

The user authorizes removing dashboard E:/Games if E: needs space, while
preserving Apps/Applications. Do not broaden that folder deletion to F:/Games
or unrelated data. Preserve existing application and boot paths on E:; review
owned test artifacts against retained evidence before removing them.

The single read-only dashboard001 inventory accessed only E: and F: directory
listings (plus the existing F: ownership marker). E: has Applications and no
top-level Games directory. F: has Games, Applications and the native Windows
installation. FTP LIST completion did not report free capacity. No current
free-space measurement, deletion, Windows launch or driver change occurred.
No C: access was made. Deleting E:/Games would not address the C: warning.

Next packaging work should target E: without assuming an extended F: partition
exists. Prove boot/system-path/registry and capacity behavior in a fresh stock-
layout emulator fixture before any physical relocation. Keep current working
installation, immutable releases and rollbacks intact. A stock-drive profile
must not be advertised as supported solely because its file sizes fit.
