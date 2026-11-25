import os
import json
from PIL import Image

os.makedirs("graphics", exist_ok=True)

# Paleta 15 cores + indice 0 magenta (#FF00FF) compativel com BGR555
PALETTE = [
    (255, 0, 255),   # 0: Transparente
    (24, 32, 24),    # 1: Contorno escuro
    (56, 80, 40),    # 2: Musgo escuro
    (88, 120, 56),   # 3: Musgo medio
    (128, 160, 80),  # 4: Musgo claro
    (80, 88, 96),    # 5: Pedra escura
    (136, 144, 152), # 6: Pedra media
    (192, 200, 208), # 7: Pedra clara
    (24, 88, 216),   # 8: Lolo azul escuro
    (56, 144, 248),  # 9: Lolo azul claro
    (216, 72, 136),  # 10: Lala rosa escuro
    (248, 136, 184), # 11: Lala rosa claro
    (224, 40, 40),   # 12: Vermelho (coracao/laco)
    (248, 208, 48),  # 13: Dourado (chave)
    (248, 248, 248), # 14: Branco
    (136, 88, 48),   # 15: Marrom (bau/porta)
]

def flat_palette():
    p = []
    for rgb in PALETTE:
        p.extend(rgb)
    p.extend([0] * (768 - len(p)))
    return p

def save_4bpp(name, w, h, pixels, meta):
    img = Image.new("P", (w, h), 0)
    img.putpalette(flat_palette())
    img.putdata(pixels)
    img.save(f"graphics/{name}.bmp", format="BMP")
    with open(f"graphics/{name}.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

def make_sprite_16(draw_fn):
    buf = [0] * (16 * 16)
    def px(x, y, c):
        if 0 <= x < 16 and 0 <= y < 16:
            buf[y * 16 + x] = c
    draw_fn(px)
    return buf

# Lolo 16x16
def draw_lolo(px):
    for y in range(2, 14):
        for x in range(2, 14):
            d = (x - 7.5) ** 2 + (y - 7.5) ** 2
            if d <= 34:
                px(x, y, 1 if d > 24 else (9 if y < 8 else 8))
    for ex in (5, 9):
        for y in range(5, 9):
            px(ex, y, 14)
            px(ex + 1, y, 14)
        px(ex + 1, 7, 1)

# Lala 16x16
def draw_lala(px):
    for y in range(3, 14):
        for x in range(2, 14):
            d = (x - 7.5) ** 2 + (y - 8.5) ** 2
            if d <= 32:
                px(x, y, 1 if d > 22 else (11 if y < 9 else 10))
    for x in range(4, 12):
        px(x, 2, 12)
        px(x, 3, 12)
    for ex in (5, 9):
        px(ex, 7, 14)
        px(ex, 8, 1)

# Bloco empurravel 16x16
def draw_block(px):
    for y in range(16):
        for x in range(16):
            if x in (0, 15) or y in (0, 15):
                px(x, y, 1)
            elif x == 1 or y == 1:
                px(x, y, 7)
            elif x == 14 or y == 14:
                px(x, y, 5)
            else:
                px(x, y, 6)

# Coracao 16x16
def draw_heart(px):
    pts = [
        "....11....11....",
        "...1CC1..1CC1...",
        "..1CECC11CCCC1..",
        "..1CECCCCCCCC1..",
        "..1CCCCCCCCCC1..",
        "...1CCCCCCCC1...",
        "....1CCCCCC1....",
        ".....1CCCC1.....",
        "......1CC1......",
        ".......11......."
    ]
    cmap = {".": 0, "1": 1, "C": 12, "E": 14}
    for y, row in enumerate(pts):
        for x, ch in enumerate(row):
            px(x, y + 3, cmap[ch])

# Fundo 256x256 da Camara 1 (Pantano)
bg = [2] * (256 * 256)
for ty in range(10):
    for tx in range(15):
        is_wall = tx in (0, 14) or ty in (0, 9)
        for py in range(16):
            for px_i in range(16):
                x, y = tx * 16 + px_i, ty * 16 + py
                if is_wall:
                    c = 1 if (px_i in (0, 15) or py in (0, 15)) else (4 if py < 4 else 2)
                else:
                    c = 3 if ((tx + ty) % 2 == 0) else 2
                    if px_i == 0 or py == 0:
                        c = 2
                bg[y * 256 + x] = c

save_4bpp("bg_pantano", 256, 256, bg, {"type": "regular_bg", "bpp_mode": "bpp_4"})
save_4bpp("lolo", 16, 16, make_sprite_16(draw_lolo), {"type": "sprite", "bpp_mode": "bpp_4"})
save_4bpp("lala", 16, 16, make_sprite_16(draw_lala), {"type": "sprite", "bpp_mode": "bpp_4"})
save_4bpp("bloco", 16, 16, make_sprite_16(draw_block), {"type": "sprite", "bpp_mode": "bpp_4"})
save_4bpp("coracao", 16, 16, make_sprite_16(draw_heart), {"type": "sprite", "bpp_mode": "bpp_4"})
print("Assets 4bpp gerados com sucesso.")
