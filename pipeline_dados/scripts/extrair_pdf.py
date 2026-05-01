"""
extrair_pdf.py — Script auxiliar para o grupo de coleta de dados.

FLUXO:
1. Coloque o PDF do listão em: pipeline_dados/brutos/{INSTITUICAO}/{ANO}/
2. Execute este script: python pipeline_dados/scripts/extrair_pdf.py
3. Ele gera um JSON de template em: pipeline_dados/dados_processados/{INSTITUICAO}/{ANO}/{TURNO}/
4. Preencha as notas no JSON gerado.
5. Rode: python manage.py import_course_data

DEPENDÊNCIAS:
    pip install pdfplumber
"""

import os
import json
import unicodedata

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------

RAIZ_PIPELINE   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASTA_BRUTOS    = os.path.join(RAIZ_PIPELINE, "brutos")
PASTA_DESTINO   = os.path.join(RAIZ_PIPELINE, "dados_processados")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def normalizar_nome_arquivo(texto: str) -> str:
    """Remove acentos e substitui espaços por underscores."""
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
    texto = texto.lower().strip().replace(' ', '_').replace('-', '_')
    return texto


def gerar_template_json(institution: str, year: int, course: str,
                        campus: str, degree: str, shift: str) -> dict:
    """
    Retorna o esqueleto de um JSON pronto para ser preenchido com as notas.
    Basta substituir os 0.0 pelas notas reais do listão.
    """
    codigos_por_instituicao = {
        "IFPA": ["AC", "L1", "L2", "L3", "L4", "L5", "L6", "L7", "L8"],
        "UFPA": ["AC", "PCDA", "E", "EPCD", "EQ", "EPPI", "ER", "ERPCD", "ERQ", "ERPPI"],
        "UEPA": ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"],
        "UFRA": ["AC", "LB_EP", "LB_PPI", "LB_Q", "LB_PCD", "LI_EP", "LI_PPI", "LI_PCD"],
    }

    cotas = codigos_por_instituicao.get(institution.upper(), ["AC"])

    return {
        "institution": institution.upper(),
        "year_reference": year,
        "offerings": [
            {
                "course": course,
                "campus": campus,
                "degree": degree,
                "shift": shift,
                "total_spots_filled": 0,  # <- preencher
                "competition_data": [
                    {
                        "quota_code": codigo,
                        "description": f"Cota {codigo}",  # será corrigido pelo fix_quota_descriptions
                        "spots": 0,                        # <- preencher
                        "previous_cutoff": 0.0,            # <- preencher
                        "historical_max_score": 0.0        # <- preencher
                    }
                    for codigo in cotas
                ]
            }
        ]
    }


def salvar_template(dados: dict, institution: str, year: int,
                    shift: str, course: str, campus: str):
    """Salva o JSON de template no caminho correto de dados_processados/."""
    pasta = os.path.join(
        PASTA_DESTINO,
        institution.upper(),
        str(year),
        normalizar_nome_arquivo(shift)
    )
    os.makedirs(pasta, exist_ok=True)

    nome_arquivo = f"{normalizar_nome_arquivo(course)}_{normalizar_nome_arquivo(campus)}.json"
    caminho = os.path.join(pasta, nome_arquivo)

    if os.path.exists(caminho):
        print(f"[AVISO] Arquivo já existe, pulando: {caminho}")
        return

    with open(caminho, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

    print(f"[OK] Template gerado: {caminho}")


# ---------------------------------------------------------------------------
# Exemplo de uso
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("GERADOR DE TEMPLATE JSON")
    print("Preencha os dados do curso abaixo:")
    print("=" * 60)

    institution = input("Instituição (IFPA / UFPA / UEPA / UFRA): ").strip()
    year        = int(input("Ano de referência (ex: 2026): ").strip())
    course      = input("Nome do curso (ex: Engenharia da Computação): ").strip()
    campus      = input("Campus (ex: Belém): ").strip()
    degree      = input("Grau (Bacharelado / Licenciatura / Tecnólogo): ").strip()
    shift       = input("Turno (Matutino / Vespertino / Noturno / Nao Informado): ").strip()

    dados = gerar_template_json(institution, year, course, campus, degree, shift)
    salvar_template(dados, institution, year, shift, course, campus)

    print()
    print("Proximo passo: Abra o JSON gerado e preencha as notas de corte!")
    print("Depois rode: python manage.py import_course_data")
