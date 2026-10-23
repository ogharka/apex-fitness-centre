"""Cover images for blog posts (1200 x 675). No text on covers: the title is already on the page.

A post gets its cover in this order:
  1. image:        its own photo from source/content/blog/images/
  2. cover_photo:  a photo from that folder (or assets/...) used as the cover
  3. cover_art:    one of the illustrations below (thali, protein, tub, check, dumbbell, medal, scale)
  4. otherwise a sensible default for the post's category
"""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
W, H, S = 1200, 675, 2  # drawn at 2x, then scaled down for smooth edges
RED, RED2, INK = (211, 19, 43), (240, 90, 100), (34, 36, 40)
BG, BG2 = (247, 243, 236), (239, 232, 221)

def _canvas():
    im = Image.new("RGB", (W * S, H * S), BG)
    d = ImageDraw.Draw(im)
    d.ellipse((W * S * .62, -H * S * .35, W * S * 1.25, H * S * .55), fill=BG2)   # soft shapes
    d.ellipse((-W * S * .2, H * S * .62, W * S * .35, H * S * 1.4), fill=BG2)
    return im, d

def _shadow(im, box, blur=30, alpha=70):
    sh = Image.new("L", im.size, 0)
    ImageDraw.Draw(sh).ellipse([v * S for v in box], fill=alpha)
    sh = sh.filter(ImageFilter.GaussianBlur(blur * S))
    im.paste((0, 0, 0), (0, 0), sh)

def _sc(box): return [v * S for v in box]

def _bowl(d, cx, cy, r, food, rim=(250, 250, 248)):
    d.ellipse(_sc((cx - r, cy - r, cx + r, cy + r)), fill=rim)
    d.ellipse(_sc((cx - r * .8, cy - r * .8, cx + r * .8, cy + r * .8)), fill=food)

def art_thali(im, d):
    _shadow(im, (330, 520, 900, 640))
    d.ellipse(_sc((300, 70, 900, 600)), fill=(226, 223, 216))          # steel plate rim
    d.ellipse(_sc((330, 98, 870, 572)), fill=(238, 236, 231))
    for x, y in [(470, 360), (520, 330), (560, 375), (500, 405), (585, 335), (455, 315), (540, 420), (610, 390)]:
        d.ellipse(_sc((x - 70, y - 55, x + 70, y + 55)), fill=(252, 250, 244))  # rice mound
    _bowl(d, 700, 220, 85, (228, 166, 48))       # dal
    d.ellipse(_sc((690, 200, 712, 222)), fill=(110, 150, 60))  # coriander
    _bowl(d, 760, 400, 78, (160, 82, 38))        # chicken / masu
    for x, y in [(745, 385), (780, 410), (755, 420)]: d.ellipse(_sc((x - 18, y - 14, x + 18, y + 14)), fill=(196, 112, 54))
    _bowl(d, 430, 190, 68, (108, 148, 62))       # saag / tarkari
    d.polygon(_sc((610, 520, 690, 470, 700, 480, 625, 530)), fill=(70, 140, 60))   # chilli
    d.ellipse(_sc((380, 455, 440, 515)), fill=(250, 214, 70)); d.ellipse(_sc((390, 465, 430, 505)), fill=(253, 236, 150))  # lemon

def art_protein(im, d):
    _shadow(im, (220, 540, 1000, 640), alpha=60)
    d.rounded_rectangle(_sc((270, 150, 400, 560)), radius=30 * S, fill=(250, 250, 250), outline=(214, 220, 228), width=6 * S)  # glass of milk
    d.rounded_rectangle(_sc((282, 230, 388, 548)), radius=22 * S, fill=(255, 255, 255))
    for i, (x, y) in enumerate([(500, 470), (585, 500), (545, 410)]):
        d.ellipse(_sc((x - 52, y - 66, x + 52, y + 66)), fill=(252, 248, 238), outline=(232, 226, 210), width=3 * S)
    d.ellipse(_sc((640, 400, 760, 480)), fill=(252, 248, 238)); d.ellipse(_sc((675, 418, 725, 462)), fill=(246, 178, 40))  # half egg
    _bowl(d, 860, 430, 110, (228, 166, 48))       # dal
    for x, y in [(820, 230), (890, 215), (855, 290), (925, 280)]:
        d.rounded_rectangle(_sc((x - 34, y - 34, x + 34, y + 34)), radius=10 * S, fill=(250, 240, 214), outline=(232, 218, 186), width=3 * S)  # paneer
    for x, y in [(470, 230), (500, 255), (535, 235), (515, 210), (560, 260), (480, 280)]:
        d.ellipse(_sc((x - 18, y - 12, x + 18, y + 12)), fill=(196, 140, 84))  # peanuts

def _tub(d, x, y, w=300, h=380):
    d.rounded_rectangle(_sc((x, y + 60, x + w, y + h)), radius=46 * S, fill=(52, 54, 60))
    d.rounded_rectangle(_sc((x + 26, y, x + w - 26, y + 76)), radius=16 * S, fill=(30, 31, 35))
    d.rectangle(_sc((x, y + 150, x + w, y + 270)), fill=(250, 250, 250))
    d.rectangle(_sc((x, y + 150, x + w, y + 164)), fill=RED)
    d.rounded_rectangle(_sc((x + 40, y + 190, x + w - 120, y + 206)), radius=8 * S, fill=(70, 72, 78))
    d.rounded_rectangle(_sc((x + 40, y + 222, x + w - 60, y + 236)), radius=7 * S, fill=(200, 200, 200))

def art_tub(im, d):
    _shadow(im, (330, 560, 900, 650))
    _tub(d, 360, 170)
    d.ellipse(_sc((700, 480, 900, 580)), fill=(250, 250, 250))            # powder heap
    d.rounded_rectangle(_sc((690, 430, 820, 500)), radius=26 * S, fill=(235, 72, 84))  # scoop
    d.ellipse(_sc((700, 410, 810, 470)), fill=(252, 252, 252))
    d.rounded_rectangle(_sc((810, 455, 960, 475)), radius=10 * S, fill=(235, 72, 84))

def art_check(im, d):
    _shadow(im, (300, 560, 880, 650))
    _tub(d, 330, 170)
    cx, cy, r = 760, 330, 120                                                # magnifying glass
    d.ellipse(_sc((cx - r, cy - r, cx + r, cy + r)), fill=(225, 238, 245), outline=INK, width=22 * S)
    d.line(_sc((cx + 85, cy + 85, cx + 210, cy + 210)), fill=INK, width=34 * S)
    d.ellipse(_sc((cx - 70, cy - 80, cx - 30, cy - 40)), fill=(255, 255, 255))
    d.ellipse(_sc((970, 470, 1090, 590)), fill=(31, 190, 92))                  # verified tick
    d.line(_sc((1000, 532, 1024, 556, 1062, 505)), fill=(255, 255, 255), width=14 * S, joint="curve")

def art_dumbbell(im, d):
    _shadow(im, (170, 500, 1020, 610))
    d.rounded_rectangle(_sc((290, 405, 690, 435)), radius=15 * S, fill=(150, 152, 158))      # dumbbell bar
    for x, w, h in [(210, 60, 250), (270, 40, 200), (670, 40, 200), (710, 60, 250)]:
        d.rounded_rectangle(_sc((x, 420 - h / 2, x + w, 420 + h / 2)), radius=14 * S, fill=(40, 42, 48))
    d.ellipse(_sc((875, 210, 1005, 330)), outline=RED, width=28 * S)                           # kettlebell handle
    d.rounded_rectangle(_sc((850, 290, 1030, 545)), radius=80 * S, fill=RED)                   # kettlebell body
    d.ellipse(_sc((890, 330, 930, 370)), fill=(240, 90, 100))

def art_medal(im, d):
    _shadow(im, (420, 560, 780, 640))
    d.polygon(_sc((520, 60, 600, 60, 640, 300, 560, 300)), fill=RED)
    d.polygon(_sc((680, 60, 600, 60, 560, 300, 640, 300)), fill=RED2)
    d.ellipse(_sc((450, 260, 750, 560)), fill=(232, 182, 58)); d.ellipse(_sc((495, 305, 705, 515)), fill=(244, 206, 96))
    d.regular_polygon((600 * S, 410 * S, 70 * S), 5, rotation=90, fill=(232, 182, 58))

def art_scale(im, d):
    _shadow(im, (360, 540, 840, 630))
    d.rounded_rectangle(_sc((390, 170, 810, 560)), radius=60 * S, fill=(250, 250, 250), outline=(220, 220, 220), width=4 * S)
    d.rounded_rectangle(_sc((500, 220, 700, 300)), radius=18 * S, fill=INK)
    d.rounded_rectangle(_sc((530, 245, 670, 275)), radius=8 * S, fill=(120, 220, 160))
    d.ellipse(_sc((850, 420, 990, 560)), fill=RED); d.ellipse(_sc((895, 465, 945, 515)), fill=(250, 250, 250))  # tape roll
    d.rounded_rectangle(_sc((900, 535, 1080, 560)), radius=6 * S, fill=(240, 90, 100))

ARTS = {"thali": art_thali, "protein": art_protein, "tub": art_tub, "check": art_check,
        "dumbbell": art_dumbbell, "medal": art_medal, "scale": art_scale}
CATEGORY_DEFAULT = {"Supplements": ("art", "tub"), "Diet": ("art", "thali"), "Training": ("art", "dumbbell"),
                    "Weight loss": ("art", "scale"), "Competitions": ("art", "medal"),
                    "Gyms in Nepal": ("photo", "assets/gym-hero.jpg"), "Fitness careers": ("photo", "assets/gym-machines.jpg"),
                    "Influencers and athletes": ("photo", "assets/gym-free-weights.jpg")}

def make_cover(path_out, category="", art=None, photo=None, **_):
    if not art and not photo:
        kind, val = CATEGORY_DEFAULT.get(category, ("art", "dumbbell"))
        if kind == "art": art = val
        else: photo = os.path.join(HERE, val)
    if photo and os.path.exists(photo):
        im = ImageOps.fit(Image.open(photo).convert("RGB"), (W, H), Image.LANCZOS, centering=(0.5, 0.45))
    else:
        im, d = _canvas()
        ARTS.get(art, art_dumbbell)(im, d)
        im = im.resize((W, H), Image.LANCZOS)
    os.makedirs(os.path.dirname(path_out), exist_ok=True)
    im.save(path_out + ".webp", "WEBP", quality=82, method=6)
    im.save(path_out + ".jpg", "JPEG", quality=86, optimize=True, progressive=True)
    return (W, H)
