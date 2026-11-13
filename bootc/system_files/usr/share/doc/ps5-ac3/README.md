# Live 5.1 over HDMI (Dolby Digital) — experimental

The PS5's HDMI bridge (VERDE) takes stereo LPCM or a compressed bitstream from Linux, not multichannel LPCM.
`ps5-audio-51` gives games and apps a 5.1 output and encodes it live to Dolby Digital (AC-3, 640 kbit/s),
sent over HDMI as an IEC 61937 bitstream. Your TV, soundbar or receiver decodes it.

Off by default. Per user:

    ps5-audio-51 enable     # then pick "Dolby Digital 5.1 (HDMI)" as the output
    ps5-audio-51 restart    # also works as a Steam shortcut, no terminal needed
    ps5-audio-51 status
    ps5-audio-51 disable    # back to stereo

## How it works

    apps -> ps5-ac3-sink (6 ch null sink) -> pw-record -> ffmpeg AC-3 -f spdif -> prefill (128 ms)
         -> pw-play (ps5-ac3-out) -> ps5-hdmi-bitstream (ALSA hdmi:0 opened with AES0=0x06)

- `ps5-ac3.service` (user) runs the pipe; `ps5-ac3-watchdog.service` stops it if the IEC958 status loses the
  non-audio bit (AES0 != 0x06), so the receiver never gets the bitstream as PCM, and re-arms it on a new EDID;
  `ps5-ac3-health.timer` (15 s) brings back PipeWire, pulse and the pipe after an OOM kill or a session change.
- The HDMI card profile is off while the 5.1 runs; the bitstream sink owns hdmi:0.
- Audio services get `OOMScoreAdjust=-100`; the rest of the session stays at 200.

## Known limits

- Dolby Digital is lossy. Latency was not measured; the start buffer alone holds 128 ms.
- After PipeWire restarts, Steam may lose its list of outputs (restart Steam) and games already running lose
  sound. Chromium's audio is restarted by the health check.
- Do not select "HDMI bitstream (internal, do not select)" in Steam: it is the bitstream's own output.
- Waits for HDMI to settle (20 s without a new EDID, 60 s after start) before playing: with audio on hdmi:0
  during Game Mode's first modeset, the driver's re-arm can loop without picture.

## Tested

One PS5 Slim (CFI-2115), PS5 Bazzite Deck v2.10, Samsung HW-Q930F soundbar over HDMI, with the same scripts
running from the user's home before they were packaged here. The packaged paths (/usr/libexec, /usr/lib/systemd/user)
have not run yet. Results so far (3 passes count as passed): games leaving without lasting stutter 3/3
(with node.lock-quantum); AES0=0x06 and six channels reaching the encoder checked in 2 games (2026-11-13);
OOM kill, cold start, session change and channel-by-channel speaker check not passed 3/3 yet.
