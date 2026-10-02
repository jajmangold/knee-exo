# -*- coding: utf-8 -*-
"""Assemble a rendered PNG sequence into a looping GIF.

    python tools/gif.py C:/Users/Josh/KneeExo_render/anim renders/anim

One GIF per subdirectory of the source, named after it. The frame rate matches the published set:
32 frames at 20 fps, so the cycle is 1.6 s. No duplicated end frame -- the pose law
(theta = 52 - 52 cos(2 pi i / N)) already returns to its start, so repeating the last frame would
produce a visible hitch at the loop point.

Palette: ONE adaptive palette, derived from the middle frame and applied to all of them, with
dithering off. Two reasons, and the second is the one that matters for file size:

  * a render of grey aluminium and blue PETG on a pale ground dithers badly -- the noise reads as
    surface texture that is not in the model, which on a technical image is worse than banding;
  * per-frame palettes defeat delta encoding. Quantising each frame on its own shifts colour
    indices between frames, so almost every pixel differs even where the image does not, and the
    GIF comes out four to five times larger than it needs to be. One palette plus disposal=1 lets
    the encoder store only what moved.
"""
import glob
import os
import sys

from PIL import Image

SRC = sys.argv[1] if len(sys.argv) > 1 else r"C:/Users/Josh/KneeExo_render/anim"
DST = sys.argv[2] if len(sys.argv) > 2 else "renders/anim"
MS = int(sys.argv[3]) if len(sys.argv) > 3 else 50          # 20 fps
COLORS = int(os.environ.get("KX_COLORS", "128"))            # 128 is plenty for six materials

if not os.path.isdir(DST):
    os.makedirs(DST)
made = 0
for sub in sorted(os.listdir(SRC)):
    d = os.path.join(SRC, sub)
    if not os.path.isdir(d):
        continue
    files = sorted(glob.glob(os.path.join(d, "*.png")))
    if not files:
        print("  %-14s no frames" % sub)
        continue
    rgb = [Image.open(f).convert("RGB") for f in files]
    # the middle frame is the most representative: the pose law peaks there, so it carries the
    # widest spread of surfaces and angles
    pal = rgb[len(rgb) // 2].convert("P", palette=Image.ADAPTIVE, colors=COLORS,
                                     dither=Image.NONE)
    frames = [im.quantize(palette=pal, dither=Image.NONE) for im in rgb]
    out = os.path.join(DST, sub + ".gif")
    frames[0].save(out, save_all=True, append_images=frames[1:], loop=0, duration=MS,
                   optimize=True, disposal=1)
    print("  %-14s %d frames %dx%d -> %s, %.1f MB"
          % (sub, len(frames), frames[0].size[0], frames[0].size[1], out,
             os.path.getsize(out) / 1048576.0))
    made += 1
print("  %d gif(s)" % made)
