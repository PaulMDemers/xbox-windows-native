# Next after the kernel allocation/copy preflight

691,692,693 and all invoked fixtures are CLOSED. Incoming1.6 is at the HDMI
UnleashX dashboard. No hook, pending launch or owned host process; build lease
released, hardware ticket retained, automation paused. Do not repeat/recollect.
See693/REPORT.md,692/analysis001.json and691/legacy-audit002.json.

The real kernel can round the requested virtual stub address down to64KiB and
expand the returned extent. The old wrapper uses one variable for the physical
execution address and the API's in/out virtual reservation base. Its compiled
model reaches an unowned write with rounded output. This is a concrete candidate
loader defect;689's actual allocation values and failure phase remain unknown.

693 demonstrates the replacement memory contract under the kernel: retain the
physical target, returned reservation base, and high allocation pointer separately;
prove the requested page is fully contained; copy through the requested address;
release through the returned base. Actual physical stub01eff000 and low virtual
target's backing000ba000 are distinct and both copies/guards passed. Never hard-
code either address; acquire/verify fresh allocations for each new attempt.

1. Implement a separate diagnostic transition using this checked custody. Preserve
   framebuffer, descriptor, stack, source and target intervals. Keep low virtual
   target and physical execution target equal numerically across paging removal,
   while recognizing their different pre-transfer physical backing pages. Do not
   substitute the rounded reservation base into jump or relocation calculations.
2. Validate the entire executed assembly transition, including far targets, GDT/
   IDT access, stack switch, descriptor bounds and framebuffer cache visibility.
   Exercise actual linked bytes in fresh CPU fixtures with nonidentity mappings,
   relocated reservations and negative cases. Existing488 models and689 C-entry
   fixtures remain closed and are not new-path proof. Keep pre-transfer versus
   post-assembly context distinct. No silent IF/cache/mapping changes or unknown
   pending-bit clearing; describe any required transition state changes explicitly.
3. First physical native checkpoint must provide a bounded visible stage result
   independent of SMBus and must not masquerade as native encoder initialization.
   Retain all native read gates. No GPU register transplant, firmware-state borrowing,
   Windows launch or ordinary launcher promotion from kernel canary success.
4. Before a deliberate native hold, obtain current watch/reset availability. A new
   reviewed image requires a unique E/F path, exact readback and one20-second SITE
   request. Do not launch another copy of689 as a lucky retry. Networking679 and
   1080i remain tabled; original Conexant720p and packaged Windows stay untouched.

The next native transition is NOT implemented or staged yet. The source audit
also found unchecked null allocation and virtual-allocation status paths in the
old wrapper; preserve those model findings when preparing a future candidate.
