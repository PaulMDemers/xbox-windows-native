/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef XWN_STRETCH_BOUNDS_H
#define XWN_STRETCH_BOUNDS_H
/* Called after Eng, using a value snapshot made before Eng. Only constrain a
 * successful nonempty destination. NULL means the original full-clip fallback.
 * Normalize by comparison only: LONG_MIN/MAX never undergo negation/subtraction.
 * This does not change the mirrored rectangle passed to the software engine. */
static __inline const RECTL *XwnStretchDamage(BOOL ok, const RECTL *saved,
                                            RECTL *ordered)
{
    if (!ok || !saved || saved->left == saved->right || saved->top == saved->bottom)
        return NULL;
    ordered->left = saved->left < saved->right ? saved->left : saved->right;
    ordered->right = saved->left < saved->right ? saved->right : saved->left;
    ordered->top = saved->top < saved->bottom ? saved->top : saved->bottom;
    ordered->bottom = saved->top < saved->bottom ? saved->bottom : saved->top;
    return ordered;
}
#endif
