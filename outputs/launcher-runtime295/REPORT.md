# 295 matched launcher relocation startup proof

Both fresh control001 and candidate001 reached BootResetAction and BootFromDevice. At each stop the actual resident .text bytes after the mutable 64-byte image header match the reviewed ELF, paging is disabled, and ESP is above BSS and at or below the configured stack top. Candidate entry EIP is 0x02600420, ESP 0x02800000; later EIP is 0x0260d6e0, ESP 0x027fdf80. Control remains at its original locations. The captured 64-byte video state and scanout register are identical between runs.

The controller stopped before BootFromDevice performed its missing-payload lookup. This is launcher initialization evidence only: no Windows/FreeLdr payload, normal guest restart, HD timing change or physical qualification. Each run used a fresh unused official blank disk, private EEPROM, owned ports and lease. All breakpoints were removed and physical mode restored; host exit0 was orderly without fallback. All captures and frozen inputs rehashed.

Strict disk equality remains FALSE for the same one reserved-sector byte in each run. Complete 8 GiB map and 65536 overlay bytes show all filesystem bytes inherited unchanged; QCOW structure and EEPROM are unchanged. No gate waiver or writer attribution. Failed294 remains separate and immutable.
