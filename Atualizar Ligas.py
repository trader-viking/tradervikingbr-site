"""
atualizar_ligas.py — sincroniza as ligas do config.json com as que o HTML reconhece
====================================================================================

Coloque este arquivo na MESMA pasta do main_radar.py e rode:

    python atualizar_ligas.py              # mostra o que mudaria, sem gravar
    python atualizar_ligas.py --aplicar    # grava no config.json

O script:
  1. Lê o config.json atual
  2. Compara com a lista canônica do Live Desk (34 campeonatos)
  3. Mostra o que será adicionado e o que já existia
  4. Faz backup antes de gravar (config.json.bak)

Observação: o HTML analisa QUALQUER liga. Esta lista serve para o main_radar.py
saber o que baixar do Radar — é filtro de coleta, não de análise.
"""

import json
import shutil
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent
CONFIG = BASE_DIR / "config.json"

# Lista canônica — mesmos campeonatos que o index.html reconhece,
# já sem as variações duplicadas ("Premier League" vs "England Premier League")
LIGAS_LIVE_DESK = [
    # Europa · continental
    "UEFA Champions League",
    "UEFA Europa League",
    "UEFA Conference League",
    "UEFA Nations League",
    # Brasil
    "Brazil Serie A",
    "Brazil Serie B",
    "Brazil Serie C",
    "Brazil Copa do Brasil",
    # América do Sul
    "Copa Libertadores",
    "Copa Sudamericana",
    # Itália
    "Italy Serie A",
    "Italy Serie B",
    "Coppa Italia",
    # Inglaterra
    "England Premier League",
    "England Championship",
    # Espanha
    "Spain La Liga",
    "Copa del Rey",
    # Alemanha
    "Germany Bundesliga",
    "2. Bundesliga",
    # França
    "France Ligue 1",
    "Ligue 2",
    # Demais da Europa
    "Portugal Primeira Liga",
    "Netherlands Eredivisie",
    "Belgium Pro League",
    "Turkey Super Lig",
    "Scotland Premiership",
    "Switzerland Super League",
    "Austria Bundesliga",
    "Greece Super League",
    # Resto do mundo
    "Argentina Liga Profesional",
    "Mexico Liga MX",
    "USA MLS",
    "Japan J1 League",
    "Saudi Pro League",
]


# nomes curtos que o Radar às vezes usa para o mesmo campeonato
SINONIMOS = {
    "premier league": "england premier league",
    "championship": "england championship",
    "la liga": "spain la liga",
    "bundesliga": "germany bundesliga",
    "ligue 1": "france ligue 1",
    "primeira liga": "portugal primeira liga",
    "eredivisie": "netherlands eredivisie",
    "serie a": "italy serie a",
    "serie b": "italy serie b",
}


def norm(s: str) -> str:
    """Normaliza e resolve sinônimos, para não duplicar o mesmo campeonato."""
    base = " ".join(str(s).lower().split())
    return SINONIMOS.get(base, base)


def main():
    aplicar = "--aplicar" in sys.argv

    if not CONFIG.exists():
        print(f"ERRO: config.json não encontrado em {BASE_DIR}")
        print("Coloque este script na mesma pasta do main_radar.py.")
        return 1

    try:
        cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"ERRO ao ler config.json: {e}")
        return 1

    atuais = cfg.get("ligas_metodos_diretos", [])
    if not isinstance(atuais, list):
        atuais = []

    mapa_atual = {norm(l): l for l in atuais}

    novas, ja_existem = [], []
    for liga in LIGAS_LIVE_DESK:
        if norm(liga) in mapa_atual:
            ja_existem.append(liga)
        else:
            novas.append(liga)

    # ligas que você tem e não estão na lista do Live Desk
    nomes_ld = {norm(l) for l in LIGAS_LIVE_DESK}
    extras = [l for l in atuais if norm(l) not in nomes_ld]

    print("=" * 62)
    print("  SINCRONIZAÇÃO DE LIGAS · config.json")
    print("=" * 62)
    print(f"\nNo config.json hoje : {len(atuais)} liga(s)")
    print(f"Lista do Live Desk  : {len(LIGAS_LIVE_DESK)} campeonatos")

    if ja_existem:
        print(f"\n--- JÁ CONFIGURADAS ({len(ja_existem)}) ---")
        for l in ja_existem:
            print(f"    {l}")

    if novas:
        print(f"\n--- SERÃO ADICIONADAS ({len(novas)}) ---")
        for l in novas:
            print(f"  + {l}")
    else:
        print("\nNada a adicionar — já está tudo sincronizado.")

    if extras:
        print(f"\n--- SUAS, FORA DA LISTA DO LIVE DESK ({len(extras)}) ---")
        print("    (serão mantidas; o HTML analisa qualquer liga)")
        for l in extras:
            print(f"    {l}")

    final = atuais + novas
    print(f"\nTotal final: {len(final)} liga(s)")

    if not novas:
        return 0

    if not aplicar:
        print("\n" + "-" * 62)
        print("Nada foi gravado. Para aplicar de verdade:")
        print("    python atualizar_ligas.py --aplicar")
        return 0

    # backup e gravação
    backup = CONFIG.with_suffix(".json.bak")
    shutil.copy2(CONFIG, backup)
    cfg["ligas_metodos_diretos"] = final
    CONFIG.write_text(
        json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print("\n" + "=" * 62)
    print(f"  OK — {len(novas)} liga(s) adicionada(s)")
    print("=" * 62)
    print(f"\nBackup salvo em: {backup.name}")
    print("\nPróximo passo:")
    print("    python main_radar.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
