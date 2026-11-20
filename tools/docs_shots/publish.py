"""Turn captured PNGs in the out folder into the JPG + WebP pairs the docs use.

    python3 publish.py toolbar-open layers-panel      # named figures
    python3 publish.py                                # every PNG whose name a docs figure already uses
"""
import sys
from PIL import Image
import build as B
IMG = B.REPO / 'cloud' / 'static' / 'docs' / 'img'
MAXW = 1600
def publish(name):
    src = B.OUT / f'{name}.png'
    im = Image.open(src).convert('RGB')
    if im.width > MAXW:
        im = im.resize((MAXW, round(im.height * MAXW / im.width)), Image.LANCZOS)
    im.save(IMG / f'{name}.jpg', 'JPEG', quality=86, optimize=True, progressive=True)
    im.save(IMG / f'{name}.webp', 'WEBP', quality=84, method=6)
    print('published', name, im.size)
if __name__ == '__main__':
    names = sys.argv[1:] or [p.stem for p in sorted(IMG.glob('*.jpg')) if (B.OUT / f'{p.stem}.png').is_file()]
    for n in names:
        publish(n)
