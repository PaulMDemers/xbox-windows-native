#include <assert.h>
#include <limits.h>
#include <stdio.h>
#include "pci_probe.h"
static unsigned calls;
static void config_read(unsigned bus, unsigned dev, unsigned fn)
{
    assert(!(bus == 0 && dev == 0 && (fn == 1 || fn == 2)));
    assert(!(bus == 1 && dev != 0));
    ++calls;
}
int main(void)
{
    unsigned checks = 0, refused = 0;
    for (unsigned b = 0; b < 2; ++b)
        for (unsigned d = 0; d < 32; ++d)
            for (unsigned f = 0; f < 8; ++f) {
                int expected = !(b == 0 && d == 0 && (f == 1 || f == 2)) && !(b == 1 && d > 0);
                assert(xwn_pci_probe_allowed(b, d, f) == expected);
                ++checks;
                if (xwn_pci_probe_allowed(b, d, f)) config_read(b, d, f);
                else ++refused;
            }
    const unsigned bad[] = {32, 33, UINT_MAX};
    for (unsigned i = 0; i < 3; ++i) {
        assert(!xwn_pci_probe_allowed(0, bad[i], 0));
        assert(!xwn_pci_probe_allowed(1, 0, bad[i]));
        assert(!xwn_pci_probe_allowed(bad[i], 0, 0));
        checks += 3;
    }
    assert(!xwn_pci_probe_allowed(2, 0, 0));
    assert(!xwn_pci_probe_allowed(0, 0, 8));
    assert(calls == 262 && refused == 250);
    printf("{\"checks\":%u,\"allowed\":%u,\"excluded\":%u,\"passed\":true}\n", checks + 3, calls, refused);
    return 0;
}
