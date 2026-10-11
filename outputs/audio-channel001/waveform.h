/* Deterministic low-amplitude stereo identification pattern. SPDX-License-Identifier: MIT */
#ifndef CHANNEL001_WAVEFORM_H
#define CHANNEL001_WAVEFORM_H
#define CHANNEL001_FRAMES 144000U
static short channel001_sample(unsigned frame, unsigned channel, unsigned mask)
{
    unsigned period, half, phase, envelope;
    int value;
    if (frame >= 96000U || channel > 1U || mask > 3U || !(mask & (1U << channel))) return 0;
    period = channel ? 80U : 120U;
    half = period / 2U;
    phase = frame % period;
    if (phase >= half) phase = period - 1U - phase;
    value = ((int)phase * 2 - ((int)half - 1)) * 32;
    envelope = frame < 480U ? frame : (frame >= 95520U ? 95999U - frame : 480U);
    return (short)(value * (int)envelope / 480);
}
#endif
