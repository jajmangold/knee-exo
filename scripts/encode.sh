#!/bin/sh
set -e
D=/c/Users/Josh/KneeExo_anim
N=$(ls "$D/jpg" | wc -l)
echo "encoding $N frames"
ffmpeg -y -loglevel error -framerate 30 -start_number 1 -i "$D/jpg/f_%04d.jpg" \
  -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -movflags +faststart \
  "$D/KneeExo_assembly_1080p.mp4"
ffmpeg -y -loglevel error -framerate 30 -start_number 1 -i "$D/jpg/f_%04d.jpg" \
  -vf "scale=960:-2" -c:v libx264 -preset slow -crf 25 -pix_fmt yuv420p \
  "$D/KneeExo_assembly_960.mp4"
ls -la "$D"/*.mp4
