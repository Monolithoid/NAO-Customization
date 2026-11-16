# NAO dance — transparent arm-wave loop

A compact arm-wave cycle extracted from the user-provided `nao-dance.mp4`,
with the background removed frame by frame. This is an animation asset for a
future Plymouth theme; the existing `nao-bounce` prototype is unchanged.

## Assets

- `assets/frames/frame-01.png` through `frame-20.png`: RGBA image sequence,
  300 × 360, intended for playback at 30 fps (0.667 seconds).
- `assets/nao-wave-transparent.apng`: lossless looping preview with full alpha.
- `assets/nao-wave.gif`: transparent looping preview at 15 fps. GIF has binary
  transparency and a limited palette; use the PNG frames for the actual theme.
- `assets/nao-wave.mp4`: original cropped reference, no audio. MP4 retains the
  background and is kept only as the reproducible source for segmentation.

![Transparent loop preview](assets/nao-wave.gif)

## Selection and source

The selection starts at frame 49 (1.633 seconds) of the uploaded 20-second clip
and ends before frame 69 (2.300 seconds). Assuming the uploaded clip begins at
5:33 of the source video, this corresponds approximately to 5:34.633–5:35.300.
Source reference: https://www.youtube.com/watch?v=2laujomh0JY&t=333s

The robot raises and lowers its arm once. The cut was selected by inspecting
frames and comparing nearby poses at the loop boundary. It is a short practical
cycle, not a claim of a mathematically shortest or perfectly seamless loop.

## Reproduce

With FFmpeg installed, from this directory, replace `/path/to/nao-dance.mp4`
with the original uploaded clip:

```sh
ffmpeg -i /path/to/nao-dance.mp4 \
  -vf 'trim=start_frame=49:end_frame=69,setpts=N/(30*TB),crop=900:1080:450:0,scale=300:360' \
  -an -r 30 -fps_mode cfr -c:v libx264 -crf 18 -pix_fmt yuv420p \
  -movflags +faststart assets/nao-wave.mp4
```

Create a Python virtual environment outside the checkout and install
`rembg[cpu]==2.0.87`. The segmentation helper uses the `birefnet-general-lite`
model, downloaded and checksum-verified by rembg on first use. Model weights are
not committed and are not required to play the exported animation. CPU processing
can take several minutes and substantial memory.

```sh
mkdir -p /tmp/nao-wave-input
ffmpeg -i assets/nao-wave.mp4 /tmp/nao-wave-input/frame-%02d.png
# Run with the Python executable from the virtual environment:
python tools/remove_background.py /tmp/nao-wave-input assets/frames
ffmpeg -framerate 30 -i assets/frames/frame-%02d.png \
  -plays 0 -f apng assets/nao-wave-transparent.apng
ffmpeg -framerate 30 -i assets/frames/frame-%02d.png \
  -filter_complex '[0:v]fps=15,split[a][b];[a]palettegen=reserve_transparent=1[p];[b][p]paletteuse=alpha_threshold=128' \
  -loop 0 -gifflags -offsetting assets/nao-wave.gif
```

## Validation and next step

The reference has 20 video frames at 30 fps, a 0.667-second duration and no audio.
The transparent sequence is checked for frame count, dimensions, and alpha;
its frames are reviewed against a dark background to check the silhouette.
Automatic segmentation may leave minor edge artifacts, especially around fingers
and moving arms. This low-resolution video is not a studio-quality cutout.

Plymouth's script plugin needs an image sequence rather than MP4/GIF playback.
The PNG sequence is ready for integration; theme integration and runtime
validation in Plymouth remain pending.

The footage was supplied by the user from the linked video. No ownership or
redistribution license is asserted here; the source video's terms still apply.
