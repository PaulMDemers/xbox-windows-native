from pathlib import Path
p=Path('/home/paul/xbox-windows-native/sources/reactos/boot/freeldr/freeldr/ntldr/winldr.c')
s=p.read_text()
s=s.replace('XwnHandoffRecord[20]', 'XwnHandoffRecord[23]')
s=s.replace('#define XWN_FB_BYTES (640 * 480 * sizeof(ULONG))', 'static ULONG XwnFramebufferBytes;')
s=s.replace('XWN_FB_BYTES','XwnFramebufferBytes')
s=s.replace('    for (Char = 0; Text[Char] && Char < 74; ++Char)', '    if (Row >= XwnDisplayHeight / 16) return;\n    for (Char = 0; Text[Char] && Char < 74; ++Char)')
s=s.replace('(Row * 16 + Y) * 640 + (Char + 3) * 8 + X', '(Row * 16 + Y) * (XwnDisplayPitch / 4) + (Char + 3) * 8 + X')
s=s.replace('Index < 640 * 480', 'Index < XwnFramebufferBytes / sizeof(ULONG)')
s=s.replace('guard details v2', 'guard details v3')
s=s.replace('Expected: width 640, height 480, pitch 2560', 'Allowed: 640x480/2560 or 1024x576/4096')
s=s.replace('Expected: page-aligned FB in 03c00000..03ed4000', 'Expected: page-aligned FB wholly within top 4 MiB')
a='''    if (Width != 640 || Height != 480 || Pitch != 640 * 4 ||
        (XwnPagingFramebuffer & 0xFFF) || XwnPagingFramebuffer < 0x03C00000 ||
        XwnPagingFramebuffer > 0x04000000 - XwnFramebufferBytes ||
        XwnLookupPages != 0x3C00)
        XwnPagingStop("unsupported framebuffer or RAM layout");'''
b='''    /* These are the two observed Xromwell modes, both packed 32-bit pixels.
     * Bound dimensions/pitch before multiplication or framebuffer access. */
    if (!((Width == 640 && Height == 480 && Pitch == 2560) ||
          (Width == 1024 && Height == 576 && Pitch == 4096)))
        XwnPagingStop("unsupported display geometry");
    XwnFramebufferBytes = Pitch * Height;
    if ((XwnPagingFramebuffer & 0xFFF) || (XwnFramebufferBytes & 0xFFF) ||
        XwnPagingFramebuffer < 0x03C00000 ||
        XwnPagingFramebuffer > 0x04000000 - XwnFramebufferBytes ||
        XwnLookupPages != 0x3C00)
        XwnPagingStop("framebuffer outside reserved RAM layout");'''
assert a in s;s=s.replace(a,b)
s=s.replace('    XwnHandoffRecord[18] = XwnFramebufferBytes;', '    XwnHandoffRecord[18] = XwnFramebufferBytes;\n    XwnHandoffRecord[20] = XwnDisplayWidth;\n    XwnHandoffRecord[21] = XwnDisplayHeight;\n    XwnHandoffRecord[22] = XwnDisplayPitch;')
s=s.replace('    XwnPagingText(19, "Diagnostic halted. Photograph this screen, then reboot.", 0xFFFFFFFF);', '''    RtlStringCbPrintfA(Text, sizeof(Text), "Display: %lux%lu  Pitch: %lu  Mapped pages: %lu",
                      XwnDisplayWidth, XwnDisplayHeight, XwnDisplayPitch,
                      XwnFramebufferBytes >> 12);
    XwnPagingText(17, Text, 0xFFFFFFFF);
    XwnPagingText(20, "Diagnostic halted. Photograph this screen, then reboot.", 0xFFFFFFFF);''')
p.write_text(s)
