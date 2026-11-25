#!/usr/bin/env python3
"""Valida todos os pares graphics/*.json + graphics/*.bmp para o pipeline Butano."""
import json
import struct
import sys
from pathlib import Path


def validate_pair(json_path: Path) -> list[str]:
    errs = []
    bmp_path = json_path.with_suffix(".bmp")
    if not bmp_path.exists():
        return [f"BMP ausente para {json_path.name}"]

    try:
        meta = json.loads(json_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"JSON invalido ({json_path.name}): {exc}"]

    data = bmp_path.read_bytes()
    if len(data) < 54 or data[:2] != b"BM":
        return [f"{bmp_path.name}: assinatura BMP invalida"]

    header_size, width, height, planes, bpp, compression = struct.unpack_from("<IiiHHI", data, 14)
    abs_h = abs(height)

    if header_size != 40:
        errs.append(f"BITMAPINFOHEADER deve ter 40 bytes (atual: {header_size})")
    if planes != 1 or bpp not in (4, 8) or compression != 0:
        errs.append(f"Formato invalido (planes={planes}, bpp={bpp}, comp={compression})")
    if width <= 0 or abs_h <= 0 or (width % 8) != 0 or (abs_h % 8) != 0:
        errs.append(f"Dimensoes invalidas (devem ser multiplas de 8): {width}x{abs_h}")

    asset_type = meta.get("type")
    if asset_type == "sprite":
        fw = meta.get("width", width)
        fh = meta.get("height", abs_h)
        if width % fw != 0 or abs_h % fh != 0:
            errs.append(f"Spritesheet {width}x{abs_h} nao e multiplo de {fw}x{fh}")
    elif asset_type == "regular_bg":
        if width < 256 or abs_h < 256:
            errs.append(f"regular_bg deve ter ao menos 256x256 (atual: {width}x{abs_h})")
    else:
        errs.append(f"Tipo desconhecido no JSON: {asset_type}")

    return errs


def main() -> int:
    jsons = sorted(Path("graphics").glob("*.json"))
    if not jsons:
        print("ERRO: Nenhum JSON encontrado em graphics/")
        return 1

    total_errors = 0
    for jp in jsons:
        errs = validate_pair(jp)
        if errs:
            total_errors += len(errs)
            for e in errs:
                print(f"[ERRO] {jp.name}: {e}")
        else:
            print(f"[OK]   {jp.stem}.bmp + .json")

    print(f"Validacao concluida: {len(jsons)} assets verificados, {total_errors} erro(s).")
    return 1 if total_errors else 0


if __name__ == "__main__":
    sys.exit(main())
