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
import sys

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------

RAIZ_PIPELINE   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASTA_BRUTOS    = os.path.join(RAIZ_PIPELINE, "brutos")
PASTA_DESTINO   = os.path.join(RAIZ_PIPELINE, "dados_processados")
RAIZ_PROJETO    = os.path.dirname(RAIZ_PIPELINE)

# Inicializa o Django para verificar se os dados já existem no banco
sys.path.append(RAIZ_PROJETO)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from cota_min_and_max_enem.models import CourseOffering

# ---------------------------------------------------------------------------
# Regras de Negócio (Descrições das Cotas)
# ---------------------------------------------------------------------------

DESCRICOES_COTAS = {
    "UEPA": {
        "A": "Ampla Concorrência (Grupo 1)",
        "B": "Cota Adicional Exclusiva para Pessoas com Deficiência - PcD (Grupo 2)",
        "C": "Apenas Cota Escola (Grupo 3)",
        "D": "Cota Escola + PcD (Grupo 4)",
        "E": "Cota Escola + Étnico-Racial-Quilombola (Grupo 5)",
        "F": "Cota Escola + Étnico-Racial-Quilombola + PcD (Grupo 6)",
        "G": "Cota Escola + Renda (Grupo 7)",
        "H": "Cota Escola + Renda + PcD (Grupo 8)",
        "I": "Cota Escola + Renda + Étnico-Racial-Quilombola (Grupo 9)",
        "J": "Cota Escola + Renda + Étnico-Racial-Quilombola + PcD (Grupo 10)"
    },
    "IFPA": {
        "AC": "Ampla Concorrência",
        "L1": "Escola Pública + Renda ≤ 1,5 SM + Autodeclarados Pretos, Pardos ou Indígenas (PPI)",
        "L2": "Escola Pública + Renda ≤ 1,5 SM",
        "L3": "Escola Pública + Renda > 1,5 SM + Autodeclarados Pretos, Pardos ou Indígenas (PPI)",
        "L4": "Escola Pública + Renda > 1,5 SM",
        "L5": "Escola Pública + Renda ≤ 1,5 SM + PPI + Pessoas com Deficiência (PcD)",
        "L6": "Escola Pública + Renda ≤ 1,5 SM + Pessoas com Deficiência (PcD)",
        "L7": "Escola Pública + Renda > 1,5 SM + PPI + Pessoas com Deficiência (PcD)",
        "L8": "Escola Pública + Renda > 1,5 SM + Pessoas com Deficiência (PcD)"
    },
    "UFPA": {
        "AC": "Ampla Concorrência",
        "PCDA": "Cota Adicional Exclusiva para Pessoas com Deficiência (independente da origem escolar)",
        "E": "Apenas Cota Escola",
        "EPCD": "Cota Escola + Pessoas com Deficiência (PcD)",
        "EQ": "Cota Escola + Quilombolas",
        "EPPI": "Cota Escola + Autodeclarados Pretos, Pardos ou Indígenas (PPI)",
        "ER": "Cota Escola + Renda familiar per capita ≤ 1 salário mínimo",
        "ERPCD": "Cota Escola + Renda ≤ 1 SM + Pessoas com Deficiência (PcD)",
        "ERQ": "Cota Escola + Renda ≤ 1 SM + Quilombolas",
        "ERPPI": "Cota Escola + Renda ≤ 1 SM + Autodeclarados Pretos, Pardos ou Indígenas (PPI)"
    },
    "UFRA": {
        "AC": "Ampla Concorrência",
        "LB_EP": "Cota Escola + Renda (≤ 1 salário mínimo). Sem critério de raça ou deficiência",
        "LB_PPI": "Cota Escola + Renda (≤ 1 salário mínimo) + PPI",
        "LB_Q": "Cota Escola + Renda (≤ 1 salário mínimo) + Quilombolas",
        "LB_PCD": "Cota Escola + Renda (≤ 1 salário mínimo) + PcD",
        "LI_EP": "Cota Escola + Renda Livre (sem restrição de renda). Sem critério de raça ou deficiência",
        "LI_PPI": "Cota Escola + Renda Livre + PPI",
        "LI_PCD": "Cota Escola + Renda Livre + PcD"
    }
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def curso_existe_no_banco(institution: str, year: int, course: str, campus: str, shift: str) -> bool:
    """Verifica se a oferta de curso já existe no banco de dados Django."""
    return CourseOffering.objects.filter(
        institution__iexact=institution,
        year_reference=year,
        course_name__iexact=course,
        campus__iexact=campus,
        shift__iexact=shift
    ).exists()

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
    descricoes_instituicao = DESCRICOES_COTAS.get(institution.upper(), {})

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
                        "description": descricoes_instituicao.get(codigo, f"Cota {codigo}"),
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

    if curso_existe_no_banco(institution, year, course, campus, shift):
        print(f"\n[ATENÇÃO] O curso '{course}' ({campus} - {shift}) já existe no BANCO DE DADOS para o ano {year}!")
        continuar = input("Deseja extrair/gerar o template mesmo assim? (s/n): ").strip().lower()
        if continuar != 's':
            print("Operação cancelada.")
            sys.exit(0)

    dados = gerar_template_json(institution, year, course, campus, degree, shift)
    salvar_template(dados, institution, year, shift, course, campus)

    print()
    print("Proximo passo: Abra o JSON gerado e preencha as notas de corte!")
    print("Depois rode: python manage.py import_course_data")
