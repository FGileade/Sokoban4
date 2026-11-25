#!/usr/bin/env python3
"""
Validador matematico (BFS) para Sokoban4-main/include/chambers.h.
Testa se todas as 4 camaras sao solucionaveis com as regras exatas de src/main.cpp.
"""
from collections import deque
from pathlib import Path
import re
import sys

DIRS = [(0, -1), (0, 1), (-1, 0), (1, 0)]


def parse_chambers(path: Path):
    text = path.read_text(encoding="utf-8")
    chunks = re.split(r"//\s*[1-4]\.\s+", text)[1:]
    if len(chunks) != 4:
        raise ValueError(f"Esperadas 4 camaras comentadas (// 1. ... // 4.), encontradas {len(chunks)}")

    chambers = []
    for idx, ch in enumerate(chunks, start=1):
        rows = re.findall(r'"([#.~D]{15})"', ch)
        if len(rows) != 10:
            raise ValueError(f"Camara {idx}: esperado 10 linhas de mapa, obtido {len(rows)}")

        tail = ch.split("},", 1)[1]
        m_key = re.search(r"\b(true|false)\s*,\s*\{(\d+),\s*(\d+)\}", tail)
        if not m_key:
            raise ValueError(f"Camara {idx}: falha ao ler has_key/key_pos")
        has_key = m_key.group(1) == "true"
        key_pos = (int(m_key.group(2)), int(m_key.group(3)))

        pos3 = [(int(x), int(y)) for x, y in re.findall(r"\{(\d+),\s*(\d+)\}", tail[:m_key.start()])]
        if len(pos3) < 3:
            raise ValueError(f"Camara {idx}: falha ao ler lolo_start/lala_pos/chest_pos")
        lolo_start, lala_pos, chest_pos = pos3[0], pos3[1], pos3[2]

        after_key = tail[m_key.end():]
        m_flags = re.search(r"\b(true|false)\s*,\s*(true|false)\b", after_key)
        if not m_flags:
            raise ValueError(f"Camara {idx}: falha ao ler ice_slides/water_bridges")
        ice_slides = m_flags.group(1) == "true"
        water_bridges = m_flags.group(2) == "true"

        arrays = re.findall(r"(\d+)\s*,\s*(\{\{.*?\}\})", after_key[m_flags.end():], flags=re.S)
        if len(arrays) < 3:
            raise ValueError(f"Camara {idx}: falha ao ler blocks/rocks/hearts")

        def take_pairs(cnt_str, body):
            cnt = int(cnt_str)
            pts = [(int(x), int(y)) for x, y in re.findall(r"\{(\d+),\s*(\d+)\}", body)]
            return pts[:cnt]

        blocks = tuple(take_pairs(*arrays[0]))
        rocks = set(take_pairs(*arrays[1]))
        hearts = tuple(take_pairs(*arrays[2]))

        chambers.append({
            "index": idx,
            "grid": rows,
            "lolo_start": lolo_start,
            "lala_pos": lala_pos,
            "chest_pos": chest_pos,
            "has_key": has_key,
            "key_pos": key_pos,
            "ice_slides": ice_slides,
            "water_bridges": water_bridges,
            "blocks": blocks,
            "rocks": rocks,
            "hearts": hearts,
        })
    return chambers


MAX_STATES = 2_000_000


def solve(ch: dict) -> int | None:
    """BFS sobre empurroes (Sokoban classico): o estado guarda a regiao
    alcancavel do jogador, nao cada passo. Retorna n. de empurroes,
    None se sem solucao, -1 se atingiu o limite de estados."""
    grid = ch["grid"]
    rocks = ch["rocks"]
    hearts = ch["hearts"]
    all_hearts = (1 << len(hearts)) - 1
    lala = ch["lala_pos"]
    chest = ch["chest_pos"]
    key_pos = ch["key_pos"]

    def can_walk(bridges, x, y):
        if x < 0 or x >= 15 or y < 0 or y >= 10:
            return False
        if (x, y) in rocks:
            return False
        c = grid[y][x]
        return c == "." or (c == "~" and (x, y) in bridges)

    def region(start, blocks, bridges):
        bset = set(blocks)
        seen_r = {start}
        stack = [start]
        while stack:
            x, y = stack.pop()
            for dx, dy in DIRS:
                n = (x + dx, y + dy)
                if n in seen_r or n in bset or not can_walk(bridges, *n):
                    continue
                seen_r.add(n)
                stack.append(n)
        return seen_r

    def collect(reg, hmask, key_ok):
        for hi, hp in enumerate(hearts):
            if hp in reg:
                hmask |= 1 << hi
        if key_pos in reg:
            key_ok = True
        return hmask, key_ok

    blocks0 = tuple(sorted(ch["blocks"]))
    bridges0 = frozenset()
    pos0 = tuple(ch["lolo_start"])
    reg0 = region(pos0, blocks0, bridges0)
    h0, k0 = collect(reg0, 0, not ch["has_key"])
    start = (min(reg0), blocks0, bridges0, h0, k0)
    seen = {start}
    q = deque([(start, pos0, 0)])

    while q:
        (_, blocks, bridges, hmask, key_ok), pos, pushes = q.popleft()
        reg = region(pos, blocks, bridges)
        if key_ok and hmask == all_hearts and chest in reg:
            return pushes
        for bidx, (bx0, by0) in enumerate(blocks):
            for dx, dy in DIRS:
                # jogador precisa alcancar a celula oposta ao destino do empurrao
                if (bx0 - dx, by0 - dy) not in reg:
                    continue
                bx, by = bx0 + dx, by0 + dy
                if bx < 0 or bx >= 15 or by < 0 or by >= 10 or (bx, by) in rocks:
                    continue
                if (bx, by) in blocks or (bx, by) == lala or (bx, by) == chest:
                    continue
                new_blocks = list(blocks)
                new_bridges = set(bridges)
                dest_ch = grid[by][bx]
                if dest_ch == "~" and (bx, by) not in bridges:
                    if not ch["water_bridges"]:
                        continue
                    new_blocks.pop(bidx)
                    new_bridges.add((bx, by))
                elif dest_ch == "." or (bx, by) in bridges:
                    fx, fy = bx, by
                    if ch["ice_slides"]:
                        while True:
                            sx, sy = fx + dx, fy + dy
                            if (not can_walk(bridges, sx, sy) or (sx, sy) in new_blocks
                                    or (sx, sy) == lala or (sx, sy) == chest):
                                break
                            fx, fy = sx, sy
                    new_blocks[bidx] = (fx, fy)
                else:
                    continue
                npos = (bx0, by0)  # jogador ocupa a celula original do bloco
                nb = tuple(sorted(new_blocks))
                nbr = frozenset(new_bridges)
                nreg = region(npos, nb, nbr)
                nh, nk = collect(nreg, hmask, key_ok)
                st = (min(nreg), nb, nbr, nh, nk)
                if st not in seen:
                    if len(seen) >= MAX_STATES:
                        return -1
                    seen.add(st)
                    q.append((st, npos, pushes + 1))
    return None


def main() -> int:
    header = Path("include/chambers.h")
    if not header.exists():
        print("ERRO: include/chambers.h nao encontrado.")
        return 1

    failed = False
    for ch in parse_chambers(header):
        steps = solve(ch)
        if steps == -1:
            print(f"[AVISO] Camara {ch['index']}: limite de {MAX_STATES} estados atingido (inconclusivo).")
        elif steps is None:
            print(f"[FALHA] Camara {ch['index']}: sem solucao!")
            failed = True
        else:
            print(f"[OK]    Camara {ch['index']}: solucionavel em {steps} empurrao(oes) minimos.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
