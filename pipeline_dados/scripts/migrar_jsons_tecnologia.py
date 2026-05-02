"""
Script: migrar_jsons_tecnologia.py
Propósito: Copia os JSONs da pasta dados_de-cursos (commit 4b5ce94) para
           pipeline_dados/dados_processados, seguindo a estrutura padrão:
           INSTITUIÇÃO/ANO/turno/nome_arquivo.json

           Também cria a pasta IFPA e normaliza os dados dos arquivos IFPA
           para garantir que estejam no formato esperado pelo banco.
"""

import os
import json
import shutil
import unicodedata

# ─── Caminhos ───────────────────────────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ORIGEM = os.path.join(
    PROJECT_ROOT,
    "cota_min_and_max_enem",
    "Verificador-de-notas-de-cursos-max-e-min-das-universidades-federias-metropolinas-de-bel-m-",
    "dados_de-cursos"
)

DESTINO = os.path.join(PROJECT_ROOT, "pipeline_dados", "dados_processados")

# ─── Mapeamento de turnos (normalização) ─────────────────────────────────────
TURNO_MAP = {
    "noturno":    "noturno",
    "vespertino": "vespertino",
    "matutino":   "matutino",
    "integral":   "integral",
    "sem_dados de turno": "nao_informado",
    "nao_informado": "nao_informado",
}

# ─── Helpers ─────────────────────────────────────────────────────────────────
def normaliza_texto(s: str) -> str:
    """Remove acentos e converte para lowercase com underscores."""
    nfkd = unicodedata.normalize("NFKD", s)
    sem_acento = "".join(c for c in nfkd if not unicodedata.combining(c))
    return sem_acento.lower().replace(" ", "_")


def resolve_turno(path: str) -> str:
    """Extrai o turno a partir do path relativo."""
    partes = path.lower().replace("\\", "/").split("/")
    for parte in reversed(partes[:-1]):  # ignora o arquivo (último)
        p = parte.strip()
        if p in TURNO_MAP:
            return TURNO_MAP[p]
    return "nao_informado"


def resolve_instituicao_ano(path: str):
    """
    Extrai (instituição, ano) a partir do path relativo à pasta ORIGEM.
    Ex: UFPA_2026/matutino/arquivo.json → ("UFPA", "2026")
    """
    partes = path.replace("\\", "/").split("/")
    pasta_inst = partes[0]  # ex: UFPA_2026, IFPA_2026, UEPA_2026, UFRA_BY_SISU
    if "_" in pasta_inst:
        inst, *resto = pasta_inst.split("_")
        ano = resto[0] if resto[0].isdigit() else "2026"
    else:
        inst = pasta_inst
        ano = "2026"
    return inst.upper(), ano


# ─── Lógica de normalização do JSON ──────────────────────────────────────────
def normaliza_json(data: dict, instituicao: str, ano: int, turno_inferido: str) -> dict:
    """
    Garante que o JSON tenha todos os campos obrigatórios.
    Arquivos IFPA podem estar em formato diferente — normaliza.
    """
    # Campos de topo
    if "institution" not in data:
        data["institution"] = instituicao
    if "year_reference" not in data:
        data["year_reference"] = ano

    for oferta in data.get("offerings", []):
        # Garantir campo shift
        if not oferta.get("shift"):
            oferta["shift"] = turno_inferido.capitalize()
        # Garantir campo leftover_spots (pode não existir em arquivos antigos)
        if "leftover_spots" not in oferta:
            oferta["leftover_spots"] = 0
        # Garantir competition_data presente
        if "competition_data" not in oferta:
            oferta["competition_data"] = []

    return data


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    if not os.path.exists(ORIGEM):
        print(f"[ERRO] Pasta de origem nao encontrada: {ORIGEM}")
        return

    copiados = 0
    erros = 0

    for root, dirs, files in os.walk(ORIGEM):
        for file in files:
            if not file.endswith(".json"):
                continue

            src = os.path.join(root, file)
            rel_path = os.path.relpath(src, ORIGEM)  # ex: IFPA_2026\noturno\arquivo.json

            instituicao, ano = resolve_instituicao_ano(rel_path)
            turno = resolve_turno(rel_path)

            # Ler JSON (usando prefixo \\?\ para paths longos no Windows)
            src_abs = "\\\\?\\" + os.path.abspath(src)
            try:
                with open(src_abs, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception as e:
                print(f"[AVISO] Erro ao ler {file}: {e}")
                erros += 1
                continue

            # Normalizar dados
            data = normaliza_json(data, instituicao, int(ano), turno)

            # Destino: dados_processados/INSTITUIÇÃO/ANO/turno/arquivo.json
            destino_dir = os.path.join(DESTINO, instituicao, ano, turno)
            os.makedirs(destino_dir, exist_ok=True)

            dst = os.path.join(destino_dir, file)
            try:
                with open(dst, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                print(f"[OK] {rel_path}")
                print(f"     -> {os.path.relpath(dst, PROJECT_ROOT)}")
                copiados += 1
            except Exception as e:
                print(f"[ERRO] Erro ao salvar {file}: {e}")
                erros += 1

    print()
    print("-" * 60)
    print(f"Copiados com sucesso : {copiados}")
    print(f"Erros                : {erros}")
    print("-" * 60)
    print("Agora rode: python manage.py import_course_data")


if __name__ == "__main__":
    main()
