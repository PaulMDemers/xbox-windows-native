/* SPDX-License-Identifier: MIT
 * Host-only line transport for exercising the C core through xemu qtest.
 */
#include <stdio.h>
#include <stdlib.h>
#include "smbus.h"
static unsigned request(const char *op, unsigned offset, unsigned value)
{
    unsigned reply;
    printf("%s %u %u\n", op, offset, value); fflush(stdout);
    if (scanf("%u", &reply) != 1) exit(3);
    return reply;
}
static xwn_u8 read8(void *c, unsigned o) { (void)c; return (xwn_u8)request("R8", o, 0); }
static xwn_u16 read16(void *c, unsigned o) { (void)c; return (xwn_u16)request("R16", o, 0); }
static void write8(void *c, unsigned o, xwn_u8 v) { (void)c; (void)request("W8", o, v); }
static void delay(void *c) { (void)c; (void)request("DELAY", 0, 0); }
int main(int argc, char **argv)
{
    xwn_smb_io io = {0, read8, read16, write8, delay};
    xwn_smb_reply r;
    if (argc != 3) return 2;
    r = xwn_smb_read(&io, (unsigned)strtoul(argv[1], 0, 0), (unsigned)strtoul(argv[2], 0, 0));
    printf("RESULT %u %u %u %u %u\n", r.result, r.polls, r.attempts, r.status, r.data);
    return 0;
}
