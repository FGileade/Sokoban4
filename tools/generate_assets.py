import os
import json
import struct

os.makedirs("graphics", exist_ok=True)


def snap_bgr555(rgb):
    """Alinha RGB para multiplos de 8 (fidelidade exata GBA 15-bit BGR555)."""
    return tuple((c // 8) * 8 for c in rgb)


def write_bmp_4bpp(filepath, width, height, pixels, palette):
    """Escreve arquivo BMP 4bpp nativo (16 cores exatas, sem anti-aliasing, 100% compativel com Butano/grit)."""
    assert len(palette) <= 16, "Paleta 4bpp deve ter no maximo 16 cores."
    assert width % 2 == 0, "Largura deve ser par para 4bpp."
    pal = [snap_bgr555(c) for c in palette]
    while len(pal) < 16:
        pal.append((0, 0, 0))

    row_bytes = (width + 1) // 2
    pad = (4 - (row_bytes % 4)) % 4
    stride = row_bytes + pad
    img_size = stride * height

    # Pixel data bottom-up
    pixel_bytes = bytearray()
    for y in range(height - 1, -1, -1):
        row_start = y * width
        for x in range(0, width, 2):
            hi = pixels[row_start + x] & 0x0F
            lo = pixels[row_start + x + 1] & 0x0F
            pixel_bytes.append((hi << 4) | lo)
        if pad:
            pixel_bytes.extend(b"\x00" * pad)

    # Color table (BGRA, 16 entries * 4 bytes = 64 bytes)
    color_table = bytearray()
    for r, g, b in pal:
        color_table.extend(struct.pack("<BBBB", b, g, r, 0))

    file_header_size = 14
    dib_header_size = 40
    offset = file_header_size + dib_header_size + len(color_table)
    file_size = offset + img_size

    file_header = struct.pack("<2sIHHI", b"BM", file_size, 0, 0, offset)
    dib_header = struct.pack(
        "<IIIHHIIIIII",
        dib_header_size,
        width,
        height,
        1,          # planes
        4,          # bits per pixel (4bpp)
        0,          # BI_RGB (no compression)
        img_size,
        2835,       # x ppm
        2835,       # y ppm
        16,         # colors used
        16,         # important colors
    )

    with open(filepath, "wb") as f:
        f.write(file_header)
        f.write(dib_header)
        f.write(color_table)
        f.write(pixel_bytes)


def save_asset(name, width, height, pixels, palette, meta):
    write_bmp_4bpp(f"graphics/{name}.bmp", width, height, pixels, palette)
    with open(f"graphics/{name}.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)


# =====================================================================
# PALETAS BGR555 (Indice 0 = #FF00FF transparente + 15 cores)
# =====================================================================
PAL_PANTANO = [
    (248, 0, 248),   # 0: Transparente
    (24, 32, 24),    # 1: Contorno musgo escuro
    (48, 72, 32),    # 2: Musgo sombra
    (80, 112, 48),   # 3: Musgo medio
    (120, 152, 72),  # 4: Musgo claro
    (160, 184, 104), # 5: Musgo destaque
    (64, 72, 80),    # 6: Pedra sombra
    (112, 120, 128), # 7: Pedra media
    (168, 176, 184), # 8: Pedra clara
    (88, 64, 40),    # 9: Terra escura
    (136, 96, 56),   # 10: Terra clara
    (40, 48, 40),    # 11: Fenda
    (200, 208, 160), # 12: Pedra musgo brilho
    (24, 48, 24),    # 13: Sombra profunda
    (16, 24, 16),    # 14: Preto esverdeado
    (240, 240, 224), # 15: Brilho
]

PAL_AGUA = [
    (248, 0, 248),   # 0: Transparente
    (16, 32, 64),    # 1: Contorno azul escuro
    (24, 64, 136),   # 2: Agua profunda
    (32, 104, 192),  # 3: Agua media
    (64, 152, 232),  # 4: Agua clara
    (136, 208, 248), # 5: Espuma/brilho agua
    (48, 80, 120),   # 6: Parede azul sombra
    (80, 128, 176),  # 7: Parede azul media
    (128, 176, 216), # 8: Parede azul clara
    (184, 216, 240), # 9: Parede destaque
    (56, 72, 96),    # 10: Piso pedra azulada sombra
    (96, 112, 136),  # 11: Piso pedra azulada media
    (144, 160, 184), # 12: Piso pedra azulada clara
    (16, 48, 96),    # 13: Sombra profunda
    (8, 24, 48),     # 14: Preto azulado
    (232, 248, 248), # 15: Branco gelo
]

PAL_LAVA = [
    (248, 0, 248),   # 0: Transparente
    (48, 16, 16),    # 1: Contorno vinho escuro
    (128, 24, 16),   # 2: Lava escura
    (200, 48, 16),   # 3: Lava vermelha
    (240, 112, 16),  # 4: Lava laranja
    (248, 208, 48),  # 5: Lava amarela brilho
    (88, 48, 32),    # 6: Parede terracota sombra
    (144, 80, 48),   # 7: Parede terracota media
    (192, 120, 72),  # 8: Parede terracota clara
    (224, 168, 112), # 9: Parede destaque
    (72, 56, 48),    # 10: Passarela pedra sombra
    (120, 104, 96),  # 11: Passarela pedra media
    (168, 152, 136), # 12: Passarela pedra clara
    (64, 24, 16),    # 13: Fenda magma
    (32, 8, 8),      # 14: Preto avermelhado
    (248, 240, 168), # 15: Incandescente
]

PAL_GELO = [
    (248, 0, 248),   # 0: Transparente
    (24, 48, 88),    # 1: Contorno azul gelo
    (88, 152, 216),  # 2: Gelo sombra
    (136, 192, 240), # 3: Gelo medio
    (184, 224, 248), # 4: Gelo claro
    (232, 248, 248), # 5: Neve/brilho
    (48, 96, 160),   # 6: Parede gelo sombra
    (80, 136, 208),  # 7: Parede gelo media
    (128, 184, 240), # 8: Parede gelo clara
    (200, 232, 248), # 9: Parede destaque
    (64, 120, 184),  # 10: Rachadura gelo
    (112, 168, 224), # 11: Reflexo gelo
    (160, 208, 248), # 12: Piso gelo 2
    (32, 64, 120),   # 13: Sombra profunda
    (16, 32, 64),    # 14: Preto azulado
    (248, 248, 248), # 15: Branco puro
]

# Paleta compartilhada para personagens e props/inimigos (15 cores + transparente)
PAL_SPRITES = [
    (248, 0, 248),   # 0: Transparente
    (24, 24, 40),    # 1: Contorno escuro (azul-preto sel-out)
    (24, 80, 208),   # 2: Azul escuro (Lolo / Bola espinho)
    (56, 144, 248),  # 3: Azul claro (Lolo / Gelo)
    (160, 224, 248), # 4: Azul gelo destaque
    (200, 56, 120),  # 5: Rosa escuro (Lala)
    (248, 136, 184), # 6: Rosa claro (Lala)
    (216, 32, 32),   # 7: Vermelho (Coracao / Laco / Chama)
    (248, 136, 24),  # 8: Laranja (Chama / Bau)
    (248, 216, 48),  # 9: Dourado (Chave / Chama / Bau)
    (48, 144, 48),   # 10: Verde escuro (Leeper)
    (112, 216, 72),  # 11: Verde claro (Leeper)
    (112, 48, 184),  # 12: Roxo escuro (Polvo)
    (168, 96, 240),  # 13: Roxo claro (Polvo)
    (128, 136, 144), # 14: Cinza pedra / metal
    (248, 248, 248), # 15: Branco (Olhos / Brilho)
]


# =====================================================================
# MAPAS DAS 4 CAMARAS (15x10 tiles de 16x16 = 240x160)
# '#' = parede, '.' = piso, '~' = agua/lava mortal, 'D' = porta topo
# =====================================================================
CHAMBER_MAPS = {
    "bg_pantano": (
        PAL_PANTANO,
        [
            "#######D#######",
            "#.............#",
            "#.............#",
            "#.............#",
            "#.............#",
            "#.............#",
            "#.............#",
            "#.............#",
            "#.............#",
            "###############",
        ],
    ),
    "bg_agua": (
        PAL_AGUA,
        [
            "#######D#######",
            "#....~~~~~....#",
            "#....~~~~~....#",
            "#....~~~~~....#",
            "#....~~~~~....#",
            "#....~~~~~....#",
            "#....~~~~~....#",
            "#....~~~~~....#",
            "#....~~~~~....#",
            "###############",
        ],
    ),
    "bg_lava": (
        PAL_LAVA,
        [
            "#######D#######",
            "#~~~.......~~~#",
            "#~~~.......~~~#",
            "#~~~.......~~~#",
            "#.....~~~.....#",
            "#.....~~~.....#",
            "#~~~.......~~~#",
            "#~~~.......~~~#",
            "#~~~.......~~~#",
            "###############",
        ],
    ),
    "bg_gelo": (
        PAL_GELO,
        [
            "#######D#######",
            "#.............#",
            "#.............#",
            "#.............#",
            "#.............#",
            "#.............#",
            "#.............#",
            "#.............#",
            "#.............#",
            "###############",
        ],
    ),
}


def draw_bg_chamber(name, palette, layout):
    W, H = 256, 256
    buf = [14] * (W * H)

    for ty in range(10):
        for tx in range(15):
            ch = layout[ty][tx]
            variant = (tx * 7 + ty * 13) % 3
            for py in range(16):
                for px in range(16):
                    x, y = tx * 16 + px, ty * 16 + py
                    if ch == "#":
                        # Parede com relevo estilo Minish Cap (luz topo-esquerda)
                        if px == 0 or py == 0 or px == 15 or py == 15:
                            c = 1
                        elif py <= 2 or px <= 2:
                            c = 9 if (py == 1 or px == 1) else 8
                        elif py >= 13 or px >= 13:
                            c = 6
                        else:
                            # Tijolos
                            brick_line = (py == 8) or (px == 8 and py < 8) or (px == 4 and py >= 8)
                            c = 13 if brick_line else (8 if (px + py) % 5 == 0 else 7)
                    elif ch == "D":
                        # Porta/arco no topo
                        if px in (0, 15) or py == 0:
                            c = 1
                        elif px in (1, 2, 13, 14) or py in (1, 2):
                            c = 8 if py < 8 else 6
                        else:
                            c = 14 if (py > 4 and 3 <= px <= 12) else 13
                    elif ch == "~":
                        # Agua ou lava animavel/texturizada
                        wave = (px + py * 2 + variant * 3) % 8
                        if px == 0 or py == 0:
                            c = 2
                        elif wave == 0:
                            c = 5
                        elif wave in (1, 2):
                            c = 4
                        elif wave in (3, 4, 5):
                            c = 3
                        else:
                            c = 2
                    else:
                        # Piso com 3 variacoes de tile
                        if name == "bg_gelo":
                            if px == 0 or py == 0:
                                c = 2
                            elif (px + py) == 10 and variant == 1:
                                c = 5
                            elif (px + py) == 11 and variant == 1:
                                c = 4
                            elif variant == 2 and px in (4, 5) and py in (10, 11):
                                c = 10
                            else:
                                c = 4 if ((tx + ty) % 2 == 0) else 3
                        elif name == "bg_agua":
                            if px == 0 or py == 0:
                                c = 10
                            elif px == 1 or py == 1:
                                c = 12
                            else:
                                c = 11 if variant != 2 else 12
                        elif name == "bg_lava":
                            if px == 0 or py == 0:
                                c = 10
                            elif px == 1 or py == 1:
                                c = 12
                            else:
                                c = 11 if (px + py + variant) % 4 != 0 else 10
                        else:  # pantano
                            if px == 0 or py == 0:
                                c = 2
                            elif variant == 0 and px in (3, 4, 11) and py in (5, 12):
                                c = 4
                            elif variant == 1 and px in (6, 7) and py in (7, 8):
                                c = 2
                            elif variant == 2 and (px == 8 or py == 8):
                                c = 2
                            else:
                                c = 3 if ((tx + ty) % 2 == 0) else 4
                                if (px == 1 or py == 1) and c == 3:
                                    c = 4
                    buf[y * W + x] = c

    save_asset(name, W, H, buf, palette, {"type": "regular_bg", "bpp_mode": "bpp_4"})


for bg_name, (pal, mp) in CHAMBER_MAPS.items():
    draw_bg_chamber(bg_name, pal, mp)


# =====================================================================
# HELPERS PARA SPRITE SHEETS VERTICAIS (16 x 16*N)
# =====================================================================
def render_frames(frames_fn_list):
    h = 16 * len(frames_fn_list)
    buf = [0] * (16 * h)
    for idx, fn in enumerate(frames_fn_list):
        y0 = idx * 16

        def px(x, y, c, oy=y0):
            if 0 <= x < 16 and 0 <= y < 16:
                buf[(oy + y) * 16 + x] = c

        fn(px)
    return 16, h, buf


def draw_circle_body(px, cx, cy, r, c_out, c_hi, c_mid):
    for y in range(16):
        for x in range(16):
            d2 = (x - cx) ** 2 + (y - cy) ** 2
            if d2 <= r * r:
                if d2 > (r - 1.15) ** 2:
                    px(x, y, c_out)
                elif y < cy and x <= cx + 1:
                    px(x, y, c_hi)
                else:
                    px(x, y, c_mid)


# ---------------------------------------------------------------------
# LOLO (10 quadros: down0, down1, up0, up1, left0, left1, right0, right1, push, hurt)
# ---------------------------------------------------------------------
def lolo_frame(direction, step=0, hurt=False):
    def draw(px):
        oy = -1 if step == 1 else 0
        # Pes
        foot_l = 4 if step == 0 else 3
        foot_r = 10 if step == 0 else 11
        for fx in (foot_l, foot_l + 1, foot_r, foot_r + 1):
            px(fx, 13, 15)
            px(fx, 14, 1)
        # Corpo redondo azul
        draw_circle_body(px, 7.5, 7.2 + oy, 5.6, 1, 3, 2)
        if hurt:
            # Olhos X
            for d in range(3):
                px(4 + d, 5 + d + oy, 15)
                px(6 - d, 5 + d + oy, 15)
                px(9 + d, 5 + d + oy, 15)
                px(11 - d, 5 + d + oy, 15)
            px(7, 10 + oy, 7)
            px(8, 10 + oy, 7)
            return

        if direction == "down":
            for ex in (5, 9):
                for ey in range(5, 9):
                    px(ex, ey + oy, 15)
                    px(ex + 1, ey + oy, 15)
                px(ex + 1, 7 + oy, 1)
            px(7, 10 + oy, 1)
            px(8, 10 + oy, 1)
        elif direction == "up":
            # Costas (brilho no topo)
            for x in range(6, 10):
                px(x, 4 + oy, 4)
        elif direction == "left":
            for ey in range(5, 9):
                px(4, ey + oy, 15)
                px(5, ey + oy, 15)
            px(4, 7 + oy, 1)
            px(5, 10 + oy, 1)
        elif direction == "right":
            for ey in range(5, 9):
                px(10, ey + oy, 15)
                px(11, ey + oy, 15)
            px(11, 7 + oy, 1)
            px(10, 10 + oy, 1)
        elif direction == "push":
            for ex in (5, 9):
                for ey in range(5, 8):
                    px(ex, ey, 15)
                    px(ex + 1, ey, 15)
                px(ex + 1, 6, 1)
            # Maos estendidas
            px(2, 8, 15); px(2, 9, 1)
            px(13, 8, 15); px(13, 9, 1)
    return draw


lolo_frames = [
    lolo_frame("down", 0), lolo_frame("down", 1),
    lolo_frame("up", 0), lolo_frame("up", 1),
    lolo_frame("left", 0), lolo_frame("left", 1),
    lolo_frame("right", 0), lolo_frame("right", 1),
    lolo_frame("push", 0), lolo_frame("down", 0, hurt=True),
]
w, h, data = render_frames(lolo_frames)
save_asset("lolo", w, h, data, PAL_SPRITES, {
    "type": "sprite", "bpp_mode": "bpp_4", "width": 16, "height": 16
})


# ---------------------------------------------------------------------
# LALA (3 quadros: idle, walk/bounce, cheer)
# ---------------------------------------------------------------------
def lala_frame(mode=0):
    def draw(px):
        oy = -1 if mode == 1 else 0
        for fx in (5, 6, 9, 10):
            px(fx, 13, 15)
            px(fx, 14, 1)
        draw_circle_body(px, 7.5, 8.0 + oy, 5.2, 1, 6, 5)
        # Laco vermelho no topo
        for x in range(4, 12):
            px(x, 2 + oy, 7)
            px(x, 3 + oy, 7)
        px(7, 2 + oy, 9)
        px(8, 2 + oy, 9)
        px(4, 1 + oy, 1); px(11, 1 + oy, 1)
        # Olhos
        for ex in (5, 9):
            for ey in range(6, 9):
                px(ex, ey + oy, 15)
                px(ex + 1, ey + oy, 15)
            px(ex + 1, 7 + oy, 1)
        if mode == 2:
            px(7, 10 + oy, 7); px(8, 10 + oy, 7)
    return draw


w, h, data = render_frames([lala_frame(0), lala_frame(1), lala_frame(2)])
save_asset("lala", w, h, data, PAL_SPRITES, {
    "type": "sprite", "bpp_mode": "bpp_4", "width": 16, "height": 16
})


# ---------------------------------------------------------------------
# PROPS (8 quadros: 0=bloco pedra, 1=rocha fixa, 2=ponte agua,
#        3=bloco gelo, 4=coracao, 5=chave, 6=bau fechado, 7=bau aberto)
# ---------------------------------------------------------------------
def prop_stone_block(px):
    for y in range(16):
        for x in range(16):
            if x in (0, 15) or y in (0, 15):
                px(x, y, 1)
            elif x == 1 or y == 1:
                px(x, y, 15)
            elif x == 14 or y == 14:
                px(x, y, 1)
            elif x in (2, 13) or y in (2, 13):
                px(x, y, 14)
            else:
                px(x, y, 14 if (x + y) % 3 else 15)
    # Cruz/entalhe central
    for i in range(5, 11):
        px(i, 7, 1); px(7, i, 1)


def prop_rock(px):
    draw_circle_body(px, 7.5, 8.0, 6.2, 1, 15, 14)
    for x in range(5, 10):
        px(x, 6, 1)
    px(9, 7, 1); px(10, 8, 1)


def prop_bridge(px):
    for y in range(16):
        for x in range(16):
            if x in (0, 15) or y in (0, 15):
                px(x, y, 2)
            elif y in (4, 8, 12):
                px(x, y, 1)
            else:
                px(x, y, 8 if (y % 4 == 1) else 14)


def prop_ice_block(px):
    for y in range(16):
        for x in range(16):
            if x in (0, 15) or y in (0, 15):
                px(x, y, 2)
            elif x == 1 or y == 1:
                px(x, y, 15)
            elif (x + y) in (8, 9, 16):
                px(x, y, 15)
            else:
                px(x, y, 4 if y < 8 else 3)


def prop_heart(px):
    art = [
        "....11....11....",
        "...1771..1771...",
        "..17F771177771..",
        "..17F777777771..",
        "..177777777771..",
        "...1777777771...",
        "....17777771....",
        ".....177771.....",
        "......1771......",
        ".......11.......",
    ]
    cm = {".": 0, "1": 1, "7": 7, "F": 15}
    for y, row in enumerate(art):
        for x, ch in enumerate(row):
            px(x, y + 3, cm[ch])


def prop_key(px):
    art = [
        ".....11111......",
        "....1999991.....",
        "....1911191.....",
        "....1999991.....",
        ".....11911......",
        "......191.......",
        "......19111.....",
        "......19991.....",
        "......19111.....",
        "......19991.....",
        "......11111.....",
    ]
    cm = {".": 0, "1": 1, "9": 9}
    for y, row in enumerate(art):
        for x, ch in enumerate(row):
            px(x, y + 2, cm[ch])


def prop_chest(open_state):
    def draw(px):
        for y in range(3, 15):
            for x in range(2, 14):
                if x in (2, 13) or y in (3, 14):
                    px(x, y, 1)
                elif open_state and 4 <= y <= 7:
                    px(x, y, 9 if (x + y) % 2 == 0 else 15)
                elif y == 8:
                    px(x, y, 1)
                else:
                    px(x, y, 8 if y < 8 else 7)
        # Fechadura dourada
        px(7, 8, 9); px(8, 8, 9)
        px(7, 9, 9); px(8, 9, 9)
    return draw


w, h, data = render_frames([
    prop_stone_block, prop_rock, prop_bridge, prop_ice_block,
    prop_heart, prop_key, prop_chest(False), prop_chest(True),
])
save_asset("props", w, h, data, PAL_SPRITES, {
    "type": "sprite", "bpp_mode": "bpp_4", "width": 16, "height": 16
})


# ---------------------------------------------------------------------
# ENEMIES (16 quadros: 0-3 Leeper verde, 4-7 Polvo roxo, 8-11 Chama, 12-15 Bola Espinho)
# ---------------------------------------------------------------------
def enemy_leeper(f):
    def draw(px):
        dy = [0, -2, -3, -1][f]
        draw_circle_body(px, 7.5, 9.0 + dy, 4.8, 1, 11, 10)
        for ex in (5, 9):
            px(ex, 8 + dy, 15); px(ex, 9 + dy, 1)
        px(4, 13 + dy, 10); px(11, 13 + dy, 10)
    return draw


def enemy_octopus(f):
    def draw(px):
        draw_circle_body(px, 7.5, 6.2, 4.8, 1, 13, 12)
        for ex in (5, 9):
            px(ex, 5, 15); px(ex, 6, 1)
        # Tentaculos animados
        shift = f % 2
        for tx in (3, 6, 9, 12):
            px(tx, 11, 12)
            px(tx + (1 if shift else -1), 12, 13)
            px(tx, 13, 1)
    return draw


def enemy_flame(f):
    def draw(px):
        # Chama em 4 quadros
        tip_x = [7, 8, 7, 6][f]
        draw_circle_body(px, 7.5, 9.5, 4.8, 1, 8, 7)
        for y in range(2, 7):
            w_span = max(1, (y - 1))
            for x in range(tip_x - w_span // 2, tip_x + w_span // 2 + 1):
                px(x, y, 9 if y > 3 else 8)
        # Nucleo amarelo + olhos
        for y in range(8, 12):
            for x in range(6, 10):
                px(x, y, 9)
        px(6, 9, 15); px(6, 10, 1)
        px(9, 9, 15); px(9, 10, 1)
    return draw


def enemy_spiky(f):
    def draw(px):
        draw_circle_body(px, 7.5, 7.5, 4.6, 1, 3, 2)
        # Espinhos girando
        spikes_a = [(7, 1), (8, 1), (7, 14), (8, 14), (1, 7), (1, 8), (14, 7), (14, 8)]
        spikes_b = [(2, 2), (13, 2), (2, 13), (13, 13), (7, 2), (7, 13), (2, 7), (13, 7)]
        for sx, sy in (spikes_a if f % 2 == 0 else spikes_b):
            px(sx, sy, 15)
        px(5, 7, 15); px(6, 7, 1)
        px(9, 7, 15); px(10, 7, 1)
    return draw


enemy_frames = (
    [enemy_leeper(i) for i in range(4)] +
    [enemy_octopus(i) for i in range(4)] +
    [enemy_flame(i) for i in range(4)] +
    [enemy_spiky(i) for i in range(4)]
)
w, h, data = render_frames(enemy_frames)
save_asset("enemies", w, h, data, PAL_SPRITES, {
    "type": "sprite", "bpp_mode": "bpp_4", "width": 16, "height": 16
})

print("Todos os assets 4bpp (4 camaras + sprites animados) gerados com sucesso.")
