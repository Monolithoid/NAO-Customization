# NAO dance — extracted motion reference

A compact arm-wave cycle extracted from the user-provided `nao-dance.mp4`.
This is a motion reference for a future Plymouth animation, not an installed theme.
The existing `nao-bounce` prototype is unchanged.

## Assets

- `assets/nao-wave.mp4`: 20 frames at 30 fps, 0.667 seconds, 300 × 360, no audio.
- `assets/nao-wave.gif`: looping preview at 15 fps.

![Loop preview](assets/nao-wave.gif)

The selection starts at frame 49 (1.633 seconds) of the uploaded 20-second clip
and ends before frame 69 (2.300 seconds). Assuming the uploaded clip begins at
5:33 of the source video, this corresponds approximately to 5:34.633–5:35.300.
Source reference: https://www.youtube.com/watch?v=2laujomh0JY&t=333s

The robot raises and lowers its arm once. The cut was selected by inspecting
frames and comparing nearby poses at the loop boundary. It is a short practical
cycle, not a claim of a mathematically shortest or perfectly seamless loop.
The crop preserves the full robot and the original background; no background
removal has been applied. The robot's white body overlaps a bright, detailed
background, so a simple white color key would also erase parts of the robot.

## Reproduce

With FFmpeg installed, from this directory, replace `/path/to/nao-dance.mp4`
with the original uploaded clip:

```sh
ffmpeg -i /path/to/nao-dance.mp4 \
  -vf 'trim=start_frame=49:end_frame=69,setpts=N/(30*TB),crop=900:1080:450:0,scale=300:360' \
  -an -r 30 -fps_mode cfr -c:v libx264 -crf 18 -pix_fmt yuv420p \
  -movflags +faststart assets/nao-wave.mp4

ffmpeg -i assets/nao-wave.mp4 \
  -filter_complex '[0:v]fps=15,split[a][b];[a]palettegen[p];[b][p]paletteuse' \
  -loop 0 assets/nao-wave.gif
```

## Validation and next step

FFprobe confirmed 20 video frames at 30 fps, a 0.667-second duration and no audio.
The extracted frames were visually inspected. Plymouth rendering remains untested.
Plymouth's script plugin needs an image sequence rather than MP4/GIF playback;
background removal and theme integration are still pending.

The footage was supplied by the user from the linked video. No ownership or
redistribution license is asserted here; the source video's terms still apply.
