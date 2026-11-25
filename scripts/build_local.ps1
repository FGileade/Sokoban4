param([switch]$NativeMake)
$ErrorActionPreference = 'Stop'

Write-Host "[1/4] Gerando assets 4bpp..."
python tools/generate_assets.py

Write-Host "[2/4] Validando BMP/JSON..."
python tools/validate_assets.py

Write-Host "[3/4] Verificando solvabilidade das 4 camaras..."
python tools/solve_verify.py

if ($NativeMake) {
    Write-Host "[4/4] Compilando com make local..."
    make -j4
    python tools/rom_audit.py sokoban4.gba build/sokoban4.elf
} else {
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        throw "Docker nao encontrado. Use -NativeMake se tiver devkitARM local, ou envie para o GitHub Actions."
    }
    Write-Host "[4/4] Compilando via container devkitpro/devkitarm..."
    $root = (Get-Location).Path
    docker run --rm -v "${root}:/work" -w /work devkitpro/devkitarm:latest bash -lc '
        set -e
        if [ ! -f butano/butano/butano.mak ]; then
            git clone --depth 1 --branch 21.10.0 https://github.com/GValiente/butano.git butano
        fi
        export DEVKITPRO=/opt/devkitpro
        export DEVKITARM=/opt/devkitpro/devkitARM
        export PATH="$DEVKITARM/bin:$DEVKITPRO/tools/bin:$PATH"
        make -j$(nproc)
        python3 tools/rom_audit.py sokoban4.gba build/sokoban4.elf
    '
}
