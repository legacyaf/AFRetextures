#!/bin/sh
# Unpacks the footage clips into numbered frames for render.js.
cd "$(dirname "$0")/footage" || exit 1
for n in outfit logo-anim; do
  rm -rf "frames/$n"; mkdir -p "frames/$n"
  ffmpeg -v error -i "$n.mp4" -q:v 2 "frames/$n/%04d.jpg"
done
