.intel_syntax noprefix
.code32
.text
.global enter_stub
enter_stub:
 push 0xed7
 popfd
 mov eax,0x11111111
 mov ebx,0x22222222
 mov ecx,0x33333333
 mov edx,0x44444444
 mov esi,0x55555555
 mov edi,0x66666666
 mov ebp,0x77777777
 mov esp,0xdead0000
 jmp 0x2680000
.section .note.GNU-stack,"",@progbits
