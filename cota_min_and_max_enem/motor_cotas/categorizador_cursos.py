"""
Categorizador de Cursos — motor_cotas/categorizador_cursos.py
=============================================================
Mapeamento canônico: nome bruto do curso → categoria → classe CSS.
As classes CSS (cat-tecnologia, cat-exatas, etc.) estão definidas em
static/home/index.css e usam as variáveis --cat-* do :root.

Uso direto em Python:
    from .motor_cotas.categorizador_cursos import categorize_course
    info = categorize_course("ENGENHARIA DE COMPUTACAO")
    # {"category": "TECNOLOGIA", "css_class": "cat-tecnologia", "color": "#2563EB"}

Uso em template Django (recomendado):
    {% load course_tags %}
    <div class="modern-card {{ course.course_name|category_class }}">
"""

# ─── Paleta (espelho das variáveis CSS em static/home/index.css) ──────────────
CATEGORY_COLORS: dict[str, str] = {
    "TECNOLOGIA":   "#2563EB",
    "EXATAS":       "#64748B",
    "NATUREZA":     "#16A34A",
    "HUMANAS":      "#EA580C",
    "LICENCIATURA": "#9333EA",
    "OUTROS":       "#6B7280",
}

# Classe CSS correspondente (sincronizado com index.css)
CATEGORY_CSS_CLASS: dict[str, str] = {
    "TECNOLOGIA":   "cat-tecnologia",
    "EXATAS":       "cat-exatas",
    "NATUREZA":     "cat-natureza",
    "HUMANAS":      "cat-humanas",
    "LICENCIATURA": "cat-licenciatura",
    "OUTROS":       "cat-outros",
}

# ─── Mapeamento de palavras-chave → categoria ─────────────────────────────────
# Usa lista de tuplas (não dict) para preservar a ordem de prioridade.
# Palavras mais específicas primeiro para evitar falsos positivos.
# Ex: "ENGENHARIA DE PESCA" → NATUREZA antes de "ENGENHARIA" genérica → EXATAS.
COURSE_MAPPING: list[tuple[str, str]] = [
    # TECNOLOGIA
    ("SISTEMA",                        "TECNOLOGIA"),
    ("COMPUTA",                        "TECNOLOGIA"),
    ("SOFTWARE",                       "TECNOLOGIA"),
    ("INFORMACAO",                     "TECNOLOGIA"),
    ("INTELIGENCIA ARTIFICIAL",        "TECNOLOGIA"),
    ("GEOPROCESSAMENTO",               "TECNOLOGIA"),
    ("PRODUCAO MULTIMIDIA",            "TECNOLOGIA"),
    ("ANALISE E DESENVOLVIMENTO",      "TECNOLOGIA"),

    # NATUREZA (específicas antes das engenharias genéricas)
    ("MEDICINA",                       "NATUREZA"),
    ("BIOLOGICA",                      "NATUREZA"),
    ("BIOLOGIA",                       "NATUREZA"),
    ("AGRONOMIA",                      "NATUREZA"),
    ("FARMACIA",                       "NATUREZA"),
    ("NUTRICAO",                       "NATUREZA"),
    ("ODONTOLOGIA",                    "NATUREZA"),
    ("FISIOTERAPIA",                   "NATUREZA"),
    ("TERAPIA OCUPACIONAL",            "NATUREZA"),
    ("ENFERMAGEM",                     "NATUREZA"),
    ("VETERINARIA",                    "NATUREZA"),
    ("ENGENHARIA DE PESCA",            "NATUREZA"),
    ("ENGENHARIA FLORESTAL",           "NATUREZA"),
    ("ENGENHARIA DE BIOPROCESSOS",     "NATUREZA"),
    ("ENGENHARIA DE ENERGIA",          "NATUREZA"),
    ("ENGENHARIA AGRICOLA",            "NATUREZA"),
    ("ENGENHARIA AMBIENTAL",           "NATUREZA"),
    ("ZOOTECNIA",                      "NATUREZA"),
    ("AGROECOLOGIA",                   "NATUREZA"),
    ("GESTAO DE AGRONEGOCIO",          "NATUREZA"),
    ("GEST",                           "NATUREZA"),   # GESTÃO AMBIENTAL, etc.
    ("OCEANOGRAFIA",                   "NATUREZA"),
    ("GEOLOGIA",                       "NATUREZA"),

    # EXATAS (engenharias genéricas depois das específicas acima)
    ("ENGENHARIA CIVIL",               "EXATAS"),
    ("ENGENHARIA MECANICA",            "EXATAS"),
    ("ENGENHARIA ELETRICA",            "EXATAS"),
    ("ENGENHARIA QUIMICA",             "EXATAS"),
    ("ENGENHARIA NAVAL",               "EXATAS"),
    ("ENGENHARIA SANITARIA",           "EXATAS"),
    ("ENGENHARIA FERROVIARIA",         "EXATAS"),
    ("ENGENHARIA CARTOGRAFICA",        "EXATAS"),
    ("ENGENHARIA DE PRODUCAO",         "EXATAS"),
    ("ENGENHARIA DE TELECOMUNICACOES", "EXATAS"),
    ("MATEMATICA",                     "EXATAS"),
    ("ESTATISTICA",                    "EXATAS"),
    ("FISICA",                         "EXATAS"),
    ("QUIMICA",                        "EXATAS"),
    ("GEOFISICA",                      "EXATAS"),
    ("METEOROLOGIA",                   "EXATAS"),

    # HUMANAS
    ("ADMINISTRACAO",                  "HUMANAS"),
    ("ADMINISTRA",                     "HUMANAS"),
    ("DIREITO",                        "HUMANAS"),
    ("HISTORIA",                       "HUMANAS"),
    ("SERVICO SOCIAL",                 "HUMANAS"),
    ("PSICOLOGIA",                     "HUMANAS"),
    ("FILOSOFIA",                      "HUMANAS"),
    ("ECONOMIA",                       "HUMANAS"),
    ("CIENCIAS CONTABEIS",             "HUMANAS"),
    ("CIENCIAS SOCIAIS",               "HUMANAS"),
    ("TURISMO",                        "HUMANAS"),
    ("ARQUEOLOGIA",                    "HUMANAS"),
    ("MUSEOLOGIA",                     "HUMANAS"),
    ("JORNALISMO",                     "HUMANAS"),
    ("COMUNICACAO",                    "HUMANAS"),
    ("BIBLIOTECONOMIA",                "HUMANAS"),
    ("SECRETARIADO",                   "HUMANAS"),
    ("RELACOES",                       "HUMANAS"),

    # LICENCIATURA
    ("PEDAGOGIA",                      "LICENCIATURA"),
    ("LETRAS",                         "LICENCIATURA"),
    ("LICENCIATURA",                   "LICENCIATURA"),
    ("MUSICA",                         "LICENCIATURA"),
    ("TEATRO",                         "LICENCIATURA"),
    ("ARTES VISUAIS",                  "LICENCIATURA"),
    ("PRODUCAO CENICA",                "LICENCIATURA"),
    ("EDUCACAO FISICA",                "LICENCIATURA"),
    ("LIBRAS",                         "LICENCIATURA"),
    ("GEOGRAFIA",                      "LICENCIATURA"),
]


def categorize_course(course_name: str) -> dict:
    """
    Escaneia o nome bruto do curso e retorna categoria, classe CSS e cor hex.

    Args:
        course_name: nome do curso em qualquer case.

    Returns:
        dict com chaves:
            - "category"  → str  ex.: "TECNOLOGIA"
            - "css_class" → str  ex.: "cat-tecnologia"
            - "color"     → str  ex.: "#2563EB"

    Complexidade: O(k) onde k = len(COURSE_MAPPING).
    """
    course_upper = course_name.upper()

    for keyword, category in COURSE_MAPPING:
        if keyword in course_upper:
            return {
                "category":  category,
                "css_class": CATEGORY_CSS_CLASS[category],
                "color":     CATEGORY_COLORS[category],
            }

    # Fallback para cursos não mapeados
    return {
        "category":  "OUTROS",
        "css_class": "cat-outros",
        "color":     CATEGORY_COLORS["OUTROS"],
    }
