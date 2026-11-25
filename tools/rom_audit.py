#!/usr/bin/env python3
"""Auditoria estrutural de ROM GBA + medicao ELF (ROM / EWRAM / IWRAM)."""
from pathlib import Path
import shutil
import subprocess
import sys

LOGO_HEAD = bytes.fromhex("24 FF AE 51 69 9A A2 21 3D 84 82 0A 84 E4 09 AD")


def complement_check(data: bytes) -> int:
    chk = 0
    for b in data[0xA0:0xBD]:
        chk = (chk - b) & 0xFF
    return (chk - 0x19) & 0xFF


def main() -> int:
    rom = Path(sys.argv[1] if len(sys.argv) > 1 else "sokoban4.gba")
    elf = Path(sys.argv[2] if len(sys.argv) > 2 else "build/sokoban4.elf")

    if not rom.exists():
        print(f"ERRO: ROM nao encontrada: {rom}")
        return 1

    data = rom.read_bytes()
    print("=== AUDITORIA ROM GBA ===")
    print(f"Arquivo : {rom} ({len(data)} bytes / {len(data)/1024:.2f} KiB)")
    if len(data) < 192:
        print("ERRO: Arquivo menor que 192 bytes.")
        return 1

    logo_ok = data[0x04:0x14] == LOGO_HEAD
    title = data[0xA0:0xAC].split(b"\x00", 1)[0].decode("ascii", errors="replace")
    code = data[0xAC:0xB0].decode("ascii", errors="replace")
    fixed_96 = data[0xB2] == 0x96
    exp_chk = complement_check(data)
    act_chk = data[0xBD]
    chk_ok = exp_chk == act_chk

    print(f"Logo Nintendo (0x04) : {'OK' if logo_ok else 'DIVERGENTE'}")
    print(f"Titulo (0xA0)        : '{title}' | Code: '{code}'")
    print(f"Byte fixo 0x96       : {'OK' if fixed_96 else 'INVALIDO'}")
    print(f"Checksum 0xBD        : 0x{act_chk:02X} (esperado 0x{exp_chk:02X}) -> {'OK' if chk_ok else 'ERRO'}")

    if elf.exists() and shutil.which("arm-none-eabi-size"):
        print("\n=== USO REAL DE MEMORIA (arm-none-eabi-size) ===")
        print(subprocess.check_output(["arm-none-eabi-size", "-A", str(elf)], text=True).strip())

    print("\nNota: Auditoria estrutural nao substitui teste funcional no mGBA.")
    return 0 if (logo_ok and fixed_96 and chk_ok) else 1


if __name__ == "__main__":
    sys.exit(main())
