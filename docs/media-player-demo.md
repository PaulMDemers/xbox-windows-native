# Windows Media Player demo

The CES 2001 segment featuring Bill Gates and The Rock plays in Windows Media
Player 6.4 on the clean customized-SP4 Xbox emulator installation. It is a
useful demonstration of video decoding, software drawing and the audio stack.
The user also confirmed good windowed video and audible audio on the existing
physical demo. Fullscreen playback dropped a few frames but was acceptable to
the user. This physical demo is separate from the fresh emulator installation.

The private test used Giant Bomb's archived
[CES 2001 segment](https://archive.org/details/youtube-WMZa-tNwAzQ).
Microsoft's [January 6, 2001 announcement](https://news.microsoft.com/source/2001/01/06/much-anticipated-xbox-game-console-along-with-xbox-controller-and-game-demonstrations-headline-consumer-electronics-show/)
corroborates the event. This third-party footage is not included in the source
release and is not covered by the project's MIT license.

## Prepare a compatible clip

Use media you are entitled to use. The downloaded MP4 uses H.264/AAC, which is
not the stock Windows 2000 playback target. The tested derivative uses:

- MPEG-1 video, 320×240 at 29.97 fps, approximately 700 kbit/s.
- The 16:9 picture letterboxed inside the frame, without stretching.
- MPEG Layer II audio, stereo, 44.1 kHz, 128 kbit/s.
- MPEG program-stream container, `.mpg` extension, approximately 19 MB.

For a 16:9 input, a current FFmpeg installation can prepare this format:

```text
ffmpeg -i input.mp4 -map 0:v:0 -map 0:a:0 -vf "scale=320:180:flags=lanczos,pad=320:240:0:30:black,setsar=1" -r 30000/1001 -c:v mpeg1video -b:v 700k -maxrate 900k -bufsize 327680 -g 15 -pix_fmt yuv420p -c:a mp2 -ar 44100 -ac 2 -b:a 128k -f mpeg ces2001.mpg
```

## Play it

1. Confirm the partition mapping in the installation guide. On the tested E
   profile, dashboard `E:\Demo` is Windows `C:\Demo`. Leave dashboard C and the
   rollback installation untouched.
2. Copy the clip to that demo directory and verify its hash after transfer.
3. Connect the mouse before boot. The working route in the physical test was
   UnleashX File Explorer → `E:\Applications\XWNEBoot\default.xbe`. The Windows
   menu and FTP launch attempts failed despite the correct target; that launch
   issue remains unresolved. Start Windows at 720p and close the welcome
   window so it does not cover the player. Handle unsupported-device prompts
   without disabling devices.
4. Open Windows Media Player, choose **File → Open**, and select the clip. Or use
   **Start → Run**:

   ```text
   "C:\Program Files\Windows Media Player\mplayer2.exe" /play "C:\Demo\ces2001.mpg"
   ```

5. Check moving video and audible speech through the entire clip. Check the
   Windows/player volume and the TV volume. Close the player, then restart
   normally from Windows to return to the dashboard.

## Recorded result and limits

The emulator played the entire 190.8-second clip and the player exited normally.
Captured frames at approximately 84 and 157 seconds matched independently
decoded source frames. The captured emulated AC97 audio matched the full source
envelope with 0.9938 correlation; reversed/shuffled controls did not match.
Windows then restarted normally, with a clean full allocation audit and
unchanged protected binaries.

The physical follow-up completed a normal Windows restart and exact readback of
the demo and protected files. Its Ftdisk49 failure remains recorded. Windowed
playback is the recommended demo presentation; fullscreen frame drops remain.

These results do not certify exact physical stereo routing, zero dropped frames,
arbitrary codecs, DRM playback or GPU acceleration. The clean-install FATX
long-name and strict event failures remain separate release blockers.
