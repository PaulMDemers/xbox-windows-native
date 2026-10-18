/* SPDX-License-Identifier: MIT. Actual assembly, modeled Xbox NT file services. */
#include <assert.h>
#include <setjmp.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define API __attribute__((stdcall))
extern uint32_t entry498_record[24], entry498_trailer[4], entry498_state;
extern uint32_t entry498_owned, entry498_handle, entry498_iosb[2];
extern uint32_t entry498_object[3], entry498_close_attempted, entry498_close_status;
extern uint32_t entry498_status, entry498_failure_iosb, entry498_failure_info;
extern void host_invoke(void);
uint32_t seed_flags, expected_flags, expected_esp, observed[9], continued;
static uint32_t fault_call, fault_kind, call_index, close_calls, firmware_calls;
static uint32_t writes, flushes, file_bytes, cleanup_fault;
static unsigned char file_image[112];
static char sequence[16];
static jmp_buf refused;

static uint32_t enter(char kind) {
    uint32_t flags;
    __asm__ volatile("pushfl; popl %0" : "=r"(flags));
    assert(!(flags & 0x400)); /* Gate cleared DF for every modeled service. */
    assert(call_index < sizeof(sequence)-1);
    sequence[call_index++] = kind;
    return call_index == fault_call ? fault_kind : 0;
}
static uint32_t result(uint32_t f, uint32_t *io, uint32_t info) {
    assert(io == entry498_iosb);
    assert(io[0] == 0xeeeeeeee && io[1] == 0xeeeeeeee);
    if (f != 5) { io[0] = f == 2 ? 0xc0000001 : 0; io[1] = f == 3 ? info-1 : info; }
    return f == 1 ? 0xc0000001 : f == 4 ? 0x103 : 0;
}
static uint32_t API create(uint32_t *h, uint32_t access, uint32_t *obj,
                          uint32_t *io, void *size, uint32_t attrs,
                          uint32_t share, uint32_t disp, uint32_t opts) {
    uint32_t f = enter('C');
    assert(h == &entry498_handle && *h == 0 && access == 0x40100000);
    assert(obj == entry498_object && obj[0] == 0 && obj[2] == 0x40);
    uint16_t *name = (void *)(uintptr_t)obj[1];
    char *path = (void *)(uintptr_t)((uint32_t *)name)[1];
    assert(name[0] == strlen(path) && name[1] == name[0]+1);
    assert(!strcmp(path,"\\Device\\Harddisk0\\Partition1\\Applications\\XWNBoot498a\\entry.bin"));
    assert(!size && attrs == 0x80 && !share && disp == 2 && opts == 0x62);
    if (f != 1 && f != 4 && f != 6) *h = 0x123498;
    return result(f,io,2);
}
static uint32_t API write_file(uint32_t h, uint32_t event, uint32_t apc,
                              uint32_t ctx, uint32_t *io, void *buf,
                              uint32_t len, void *off) {
    uint32_t f = enter('W');
    assert(h == 0x123498 && !event && !apc && !ctx && !off);
    assert(++writes <= 2);
    assert(buf == (writes == 1 ? (void *)entry498_record : (void *)entry498_trailer));
    assert(len == (writes == 1 ? 96u : 16u));
    uint32_t n = f == 3 ? len-1 : len;
    if (f != 1 && f != 4) { assert(file_bytes+n <= 112); memcpy(file_image+file_bytes,buf,n); file_bytes += n; }
    return result(f,io,len);
}
static uint32_t API flush_file(uint32_t h, uint32_t *io) {
    uint32_t f = enter('F');
    assert(h == 0x123498 && ++flushes <= 2);
    return result(f,io,0);
}
static uint32_t API close_file(uint32_t h) {
    uint32_t f = enter('X');
    assert(h == 0x123498 && ++close_calls == 1 && entry498_close_attempted == 1);
    return f || cleanup_fault ? 0xc0000001 : 0;
}
static uint32_t API firmware(uint32_t mode) {
    assert(mode == 1 && ++firmware_calls <= 2);
    longjmp(refused,1);
}
void *DiagNtCreateFile = create, *DiagNtWriteFile = write_file;
void *DiagNtFlushBuffersFile = flush_file, *DiagNtClose = close_file;
void *DiagHalReturnToFirmware = firmware;

int main(int argc, char **argv) {
    assert(argc == 6);
    fault_call = strtoul(argv[1],0,0); fault_kind = strtoul(argv[2],0,0);
    seed_flags = strtoul(argv[3],0,0); cleanup_fault = strtoul(argv[4],0,0);
    if (!setjmp(refused)) host_invoke();
    assert(continued == (fault_call == 0));
    assert(firmware_calls == (fault_call != 0));
    assert(entry498_state == (fault_call ? (0x80000000u | fault_call) : 7));
    uint32_t expected[9] = {0x778899aa,0x66778899,0x55667788,expected_esp,
                           0x44556677,0x33445566,0x22334455,0x11223344,expected_flags};
    assert(!memcmp(entry498_record+5,expected,32));
    assert(entry498_record[4] == expected_flags);
    if (!fault_call) {
        assert(!memcmp(observed,expected,sizeof(expected)));
        assert(!strcmp(sequence,"CWFWFX") && file_bytes == 112);
        assert(entry498_owned == 1 && close_calls == 1 && entry498_close_status == 0);
    } else {
        int owns = !(fault_call == 1 && (fault_kind == 1 || fault_kind == 4 || fault_kind == 6));
        assert(entry498_owned == (uint32_t)owns && close_calls == (uint32_t)owns);
        assert(call_index == fault_call + (owns && fault_call != 6));
        assert(entry498_close_attempted == (uint32_t)owns);
        assert(entry498_status == (fault_kind == 1 ? 0xc0000001u : fault_kind == 4 ? 0x103u : 0));
    }
    FILE *out = fopen(argv[5],"wb"); assert(out);
    assert(fwrite(file_image,1,file_bytes,out) == file_bytes && !fclose(out));
    /* Reentry must refuse without changing the original body/terminal metadata. */
    uint32_t saved[24], saved_state = entry498_state, saved_calls = call_index;
    memcpy(saved,entry498_record,sizeof(saved));
    if (!setjmp(refused)) host_invoke();
    assert(firmware_calls == (fault_call ? 2u : 1u));
    assert(continued == (fault_call == 0) && call_index == saved_calls);
    assert(entry498_state == saved_state && !memcmp(saved,entry498_record,sizeof(saved)));
    printf("{\"passed\":true,\"fault_call\":%u,\"fault_kind\":%u,\"flags\":%u,\"sequence\":\"%s\",\"bytes\":%u,\"continued\":%u,\"close_calls\":%u,\"reentry_refused\":true}\n",
           fault_call,fault_kind,expected_flags,sequence,file_bytes,continued,close_calls);
    return 0;
}
