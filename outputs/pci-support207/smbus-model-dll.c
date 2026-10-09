/* SPDX-License-Identifier: MIT
 * Host DLL for calling the actual C engine against an owned paused xemu qtest.
 * This is not an NT5 driver and must never be installed in a guest.
 */
#include "smbus.h"
__declspec(dllexport) void xwn_model_read(const xwn_smb_io *io, unsigned address,
                                        unsigned command, xwn_smb_reply *reply)
{
    *reply = xwn_smb_read(io, address, command);
}
