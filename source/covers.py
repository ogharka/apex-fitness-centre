"""Branded cover images for blog posts (1200 x 675), made automatically at build time.

Front matter options in a post (all optional):
  cover_stat:  big number on the right, e.g. 3-5 g
  cover_label: small text under the number, e.g. creatine a day is enough
  cover_photo: a photo for the right side instead of a number, from source/content/blog/images/
If a post has image: (its own photo), that photo is used and no cover is made.
"""
import os, re
from PIL import Image, ImageDraw, ImageFont, ImageOps
from fontTools.ttLib import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
FD = os.path.join(HERE, "fonts")
W, H = 1200, 675
RED, INK, MUT, PANEL = (211, 19, 43), (20, 20, 22), (91, 94, 102), (245, 245, 243)
_cmap = None

def _f(name, size): return ImageFont.truetype(os.path.join(FD, name), size)

def _covered(text):
    """True if every character can be drawn with the bundled fonts (Latin only)."""
    global _cmap
    if _cmap is None: _cmap = set(TTFont(os.path.join(FD, "Archivo-ExpBlack.ttf")).getBestCmap())
    return all(ord(c) in _cmap or c.isspace() for c in text)

def _wrap(d, text, font, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= width: cur = t
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def make_cover(path_out, title, category, stat=None, label=None, photo=None):
    im = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(im)
    PX = 735  # right panel starts here
    if photo and os.path.exists(photo):
        ph = ImageOps.fit(Image.open(photo).convert("RGB"), (W - PX, H), Image.LANCZOS)
        im.paste(ph, (PX, 0))
    else:
        d.rectangle((PX, 0, W, H), fill=PANEL)
        if stat and _covered(stat):
            size = 150
            while size > 50 and d.textlength(stat, font=_f("Archivo-ExpBlack.ttf", size)) > (W - PX - 70): size -= 4
            sf = _f("Archivo-ExpBlack.ttf", size)
            lab = _wrap(d, label or "", _f("Instrument-600.ttf", 30), W - PX - 80) if label and _covered(label) else []
            block = size + 18 + len(lab) * 40
            y0 = (H - block) // 2
            d.text(((PX + W) // 2, y0 + size // 2), stat, font=sf, fill=RED, anchor="mm")
            for i, t in enumerate(lab):
                d.text(((PX + W) // 2, y0 + size + 34 + i * 40), t, font=_f("Instrument-600.ttf", 30), fill=MUT, anchor="mm")
        else:  # simple brand mark
            d.text(((PX + W) // 2, H // 2), "APEX", font=_f("Archivo-ExpBlack.ttf", 96), fill=RED, anchor="mm")
    # left side
    d.text((64, 70), "APEX", font=_f("Archivo-ExpBlack.ttf", 34), fill=RED, anchor="lm")
    d.line((190, 54, 190, 86), fill=(225, 225, 225), width=2)
    d.text((204, 61), "Fitness", font=_f("Instrument-600.ttf", 17), fill=INK, anchor="lm")
    d.text((204, 80), "Centre", font=_f("Instrument-600.ttf", 17), fill=INK, anchor="lm")
    cat = category if _covered(category) else "Blog"
    cf = _f("Instrument-700.ttf", 22)
    cw = d.textlength(cat, font=cf)
    d.rounded_rectangle((64, 130, 64 + cw + 40, 172), radius=21, fill=(253, 232, 235))
    d.text((84, 151), cat, font=cf, fill=RED, anchor="lm")
    if _covered(title):
        size = 64
        while True:
            tf = _f("Archivo-ExpBlack.ttf", size)
            lines = _wrap(d, title, tf, PX - 64 - 50)
            if (len(lines) <= 4 and len(lines) * size * 1.12 <= 330) or size <= 34: break
            size -= 2
        y = 205
        for t in lines:
            d.text((64, y), t, font=tf, fill=INK); y += int(size * 1.12)
        d.rectangle((64, y + 18, 150, 26 + y), fill=RED)
    d.text((64, H - 62), "apexfitnesscentre.shop/blog", font=_f("Instrument-500.ttf", 24), fill=MUT, anchor="lm")
    d.rectangle((0, H - 12, W, H), fill=RED)
    os.makedirs(os.path.dirname(path_out), exist_ok=True)
    im.save(path_out + ".webp", "WEBP", quality=82, method=6)
    im.save(path_out + ".jpg", "JPEG", quality=86, optimize=True, progressive=True)
    return (W, H)
