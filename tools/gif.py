# -*- coding: utf-8 -*-
"""Assemble a rendered PNG sequence into a looping GIF.

    python tools/gif.py C:/Users/Josh/KneeExo_render/anim renders/anim

One GIF per subdirectory of the source, named after it. The frame rate matches the published set:
32 frames at 20 fps, so the cycle is 1.6 s. No duplicated end frame -- the pose law
(theta = 52 - 52 cos(2 pi i / N)) already returns to its start, so repeating the last frame would
produce a visible hitch at the loop point.

Palette: adaptive, 256 colours, with dithering off. A render of grey aluminium and blue PETG on a
pale ground dithers badly -- the noise reads as surface texture that is not in the model, which for
a technical image is worse than banding.
"""
import glob
import os
import sys

from PIL import Image

SRC = sys.argv[1] if len(sys.argv) > 1 else r"C:/Users/Josh/KneeExo_render/anim"
DST = sys.argv[2] if len(sys.argv) > 2 else "renders/anim"
MS = int(sys.argv[3]) if len(sys.argv) > 3 else 50          # 20 fps

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
    frames = []
    for f in files:
        im = Image.open(f).convert("RGB")
        frames.append(im.convert("P", palette=Image.ADAPTIVE, colors=256, dither=Image.NONE))
    out = os.path.join(DST, sub + ".gif")
    frames[0].save(out, save_all=True, append_images=frames[1:], loop=0, duration=MS,
                   optimize=True, disposal=2)
    print("  %-14s %d frames %dx%d -> %s, %.1f MB"
          % (sub, len(frames), frames[0].size[0], frames[0].size[1], out,
             os.path.getsize(out) / 1048576.0))
    made += 1
print("  %d gif(s)" % made)
