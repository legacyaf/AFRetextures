# Allied Forces Instagram reel

`allied-forces-reel.mp4` is a 22 s, 1080x1920, 30 fps intro reel. The visuals
and soundtrack are generated from the files in `src/`, with no outside footage
or samples.

## Rebuilding

Needs Node with Playwright (Chromium), Python 3 with numpy, and ffmpeg.

    cd promo/src
    node render.js /tmp/frames
    python3 mkaudio.py /tmp/audio.wav
    ffmpeg -framerate 30 -i /tmp/frames/%05d.png -i /tmp/audio.wav \
      -c:v libx264 -preset slow -crf 22 -pix_fmt yuv420p \
      -af loudnorm=I=-14:TP=-1.5 -ar 48000 -c:a aac -b:a 192k \
      -movflags +faststart ../allied-forces-reel.mp4

The on-screen text and timeline are at the bottom of `src/reel.html`.
Fonts are Bebas Neue and Oswald (SIL Open Font License, see `src/fonts`).
