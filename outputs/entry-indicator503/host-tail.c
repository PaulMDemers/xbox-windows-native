
extern uint32_t entry503_state, entry503_status[6], entry503_restore_attempted;
extern uint32_t entry503_return_requested, entry503_restored[9];
extern int64_t entry503_interval;
static uint32_t led_fault, delay_fault, led_mask, delay_mask;
static char all_sequence[40];
static uint32_t all_index;
static void sequence_add(char value) {
    assert(all_index < sizeof(all_sequence)-1);
    all_sequence[all_index++] = value;
}
static uint32_t API led(uint32_t slave, uint32_t cmd, uint32_t word, uint32_t value) {
    uint32_t flags, stage;
    __asm__ volatile("pushfl; popl %0" : "=r"(flags));
    assert(!(flags&0x400) && (flags&0x200)==(expected_flags&0x200));
    assert(slave==0x20 && !word);
    if (cmd==8 && value==0xff) { stage=1; assert(entry503_state==1 && call_index==0); }
    else if (cmd==7 && value==1) { stage=2; assert(entry503_state==1 && call_index==0 && entry503_status[0]==0); }
    else if (cmd==8 && value==0x0f) { stage=3; assert(entry503_state==2 && entry498_state==7 && close_calls==1); }
    else { stage=4; assert(cmd==7 && value==0 && entry503_restore_attempted==1 && firmware_calls==0); }
    assert(!(led_mask&(1u<<stage))); led_mask|=1u<<stage;
    sequence_add((char)('0'+stage));
    return led_fault==stage ? 0xc0000001u : 0;
}
static uint32_t API delay(uint32_t mode, uint32_t alertable, const int64_t *interval) {
    uint32_t stage=entry503_state;
    assert(!mode && !alertable && interval==&entry503_interval && *interval==-20000000);
    assert(stage==1 || stage==2);
    assert(entry503_status[0]==0 && entry503_status[1]==0);
    if (stage==2) assert(entry503_status[3]==0 && entry498_state==7);
    assert(!(delay_mask&(1u<<stage))); delay_mask|=1u<<stage;
    sequence_add(stage==1?'A':'B');
    return delay_fault==stage ? 0x101u : 0;
}
void *Entry503HalWriteSMBusValue=led, *Entry503KeDelayExecutionThread=delay;

int main(int argc, char **argv) {
    assert(argc==8);
    fault_call=strtoul(argv[1],0,0);fault_kind=strtoul(argv[2],0,0);
    seed_flags=strtoul(argv[3],0,0);cleanup_fault=strtoul(argv[4],0,0);
    led_fault=strtoul(argv[5],0,0);delay_fault=strtoul(argv[6],0,0);
    if (!setjmp(refused)) host_invoke();
    assert(firmware_calls==1 && entry503_return_requested==1 && entry503_restore_attempted==1);
    assert(entry503_state==(fault_call?0x80000001u:2));
    assert(entry498_state==(fault_call?(0x80000000u|fault_call):7));
    uint32_t expected[9]={0x778899aa,0x66778899,0x55667788,expected_esp,
        0x44556677,0x33445566,0x22334455,0x11223344,expected_flags};
    assert(!memcmp(entry498_record+5,expected,32) && entry498_record[4]==expected_flags);
    if (!fault_call) {
        assert(!memcmp(entry503_restored,expected,sizeof(expected)));
        assert(!strcmp(sequence,"CWFWFX") && file_bytes==112 && close_calls==1 && entry498_close_status==0);
    } else {
        int owns=!(fault_call==1 && (fault_kind==1 || fault_kind==4 || fault_kind==6));
        assert(entry498_owned==(uint32_t)owns && close_calls==(uint32_t)owns);
        assert(call_index==fault_call+(owns && fault_call!=6));
        assert(entry498_close_attempted==(uint32_t)owns);
    }
    uint32_t expected_led=(1u<<1)|(1u<<4);
    if(led_fault!=1) expected_led|=1u<<2;
    if(!fault_call) expected_led|=1u<<3;
    assert(led_mask==expected_led);
    uint32_t expected_delay=0;
    if(led_fault!=1 && led_fault!=2) {
        expected_delay|=1u<<1;
        if(!fault_call && led_fault!=3)expected_delay|=1u<<2;
    }
    assert(delay_mask==expected_delay);
    assert(entry503_status[0]==(led_fault==1?0xc0000001u:0));
    assert(entry503_status[1]==(led_fault==1?0xeeeeeeeeu:led_fault==2?0xc0000001u:0));
    assert(entry503_status[3]==(fault_call?0xeeeeeeeeu:led_fault==3?0xc0000001u:0));
    assert(entry503_status[5]==(led_fault==4?0xc0000001u:0));
    assert(entry503_status[2]==((expected_delay&2)?(delay_fault==1?0x101u:0):0xeeeeeeeeu));
    assert(entry503_status[4]==((expected_delay&4)?(delay_fault==2?0x101u:0):0xeeeeeeeeu));
    FILE *out=fopen(argv[7],"wb");assert(out);
    assert(fwrite(file_image,1,file_bytes,out)==file_bytes && !fclose(out));
    uint32_t saved[24], statuses[6], state=entry503_state, calls=call_index, leds=led_mask, waits=delay_mask;
    memcpy(saved,entry498_record,sizeof(saved));memcpy(statuses,entry503_status,sizeof(statuses));
    if(!setjmp(refused))host_invoke();
    assert(firmware_calls==2 && entry503_state==state && call_index==calls && led_mask==leds && delay_mask==waits);
    assert(!memcmp(saved,entry498_record,sizeof(saved)) && !memcmp(statuses,entry503_status,sizeof(statuses)));
    printf("{\"passed\":true,\"file_sequence\":\"%s\",\"indicator_sequence\":\"%s\",\"led_mask\":%u,\"delay_mask\":%u,\"bytes\":%u,\"reentry_refused\":true}\n",sequence,all_sequence,led_mask,delay_mask,file_bytes);
    return 0;
}
