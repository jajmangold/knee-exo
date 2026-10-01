#!/bin/bash
# Build renders/anim/*.gif from the Cycles frame sequences.
#
# Pillow is the obvious tool and it is the wrong one here. Its GIF writer cost 3-4x the
# file size at the same dimensions and colour count, and the reason is dithering: a
# Floyd-Steinberg error pattern is different in every frame, so the interframe diff is the
# whole image and LZW has nothing to work with. Turning dithering off fixed the size
# (0.72 MB) and put visible contour banding across the blue highlights, which on smooth
# studio-lit gradients is the one artefact you cannot unsee.
#
# ffmpeg's palettegen/paletteuse solves both: one palette computed over the whole sequence
# (stats_mode=full), BAYER dithering, which is an ordered pattern and therefore identical
# frame to frame, and diff_mode=rectangle so only the changed region is rewritten.
#
#   Pillow, 64 colours, Floyd-Steinberg, disposal=2   3.66 MB
#   Pillow, 64 colours, Floyd-Steinberg, disposal=1   2.52 MB
#   Pillow, 64 colours, no dither                     0.72 MB, bands
#   ffmpeg, 64 colours, bayer scale 4                 1.13 MB, clean
#
# Frames come from scripts/222_anim_export.py (chunks 0..7) rendered through
# scripts/render_anim.py on the GPU box. 32 poses on theta = 52 - 52*cos(2*pi*i/32), so
# the cycle loops seamlessly with no duplicated end frame.
set -euo pipefail
SRC="${1:-C:/Users/Josh/AppData/Local/Temp/outanim}"
DST="${2:-$(dirname "$0")/../renders/anim}"
for seq in hero_clad hero_open knee_open; do
  ffmpeg -loglevel error -y -framerate 16 -i "$SRC/$seq/%03d.png" \
    -vf "scale=560:-1:flags=lanczos,split[a][b];\
[a]palettegen=max_colors=64:stats_mode=full[p];\
[b][p]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle" \
    -loop 0 "$DST/$seq.gif"
  printf '%-12s %s\n' "$seq" "$(du -h "$DST/$seq.gif" | cut -f1)"
done
