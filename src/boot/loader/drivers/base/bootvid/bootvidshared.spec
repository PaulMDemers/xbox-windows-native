@ stdcall VidBitBlt(ptr long long)
@ stdcall VidBufferToScreenBlt(ptr long long long long long)
@ stdcall VidCleanUp()
@ stdcall VidDisplayString(str)
@ stdcall VidDisplayStringXY(str long long long)
@ stdcall VidInitialize(long) XwnNt5VidInitialize
@ stdcall VidResetDisplay() XwnNt5VidResetDisplay
@ stdcall VidScreenToBufferBlt(ptr long long long long long)
@ stdcall VidSetScrollRegion(long long long long)
@ stdcall VidSetTextColor(long)
@ stdcall VidSolidColorFill(long long long long long)
@ stdcall XwnFbAcquire(ptr ptr)
@ stdcall XwnFbRelease(ptr ptr)
@ stdcall XwnFbReleaseOwner(ptr)
