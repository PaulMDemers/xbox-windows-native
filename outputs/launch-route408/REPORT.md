# 408: current Windows menu target verified, no mutation

Read-only inspection used the existing explicit380 menu-only dashboard C
exception: only /C/Dashboard/config.xml was read, plus the E launcher. No C
write or broader C access occurred. Full XML remains private E:/xwn408 because
it may contain dashboard settings; public report includes only target/hash.

The live configuration exactly matches380's installed SHA256 and its sole
Windows item points to E:\Applications\XWNEBoot\default.xbe. That file matches
qualified720p374 bytes6240a801... . It is the same file the user launched from
File Explorer successfully in407manual003. Therefore there is no observed stale
menu target to correct. No menu rewrite, driver change, new build or launch.

The cause of menu/FTP black-return versus successful direct-file boot is still
unknown. Prior407 events/hives/trace unchanged and local XBE bounds/digest checks
are separate evidence. Do not claim allocation failure from static unchecked
returns alone; do not infer DVD boot merely from drive noise. Preserve failures.
