from django import template
from ..motor_cotas.categorizador_cursos import categorize_course

register = template.Library()


@register.filter(name='category_class')
def category_class(nome_curso):
    """
    Retorna a classe CSS canônica da categoria do curso.
    Delega ao categorizador_cursos para manter a lógica centralizada.

    Uso no template:
        {% load curso_tags %}
        <div class="modern-card {{ curso.course_name|category_class }}">
    """
    if not nome_curso:
        return 'cat-outros'
    return categorize_course(str(nome_curso))['css_class']


# ─── Legado: mantido para compatibilidade com templates antigos ───────────────
PALAVRAS_CHAVE = {
    'engenharia': ['engenharia'],
    'saude': ['medicina', 'enfermagem', 'biol', 'fisioterapia', 'nutrição', 'nutricao', 'odonto', 'farmácia', 'farmacia', 'veterinária', 'veterinaria', 'biomedicina'],
    'tecnologia': ['computação', 'computacao', 'sistemas', 'software', 'física', 'fisica', 'matemática', 'matematica', 'estatística', 'estatistica', 'química', 'quimica', 'tecnologia'],
    'letras-artes': ['letras', 'artes', 'música', 'musica', 'dança', 'danca', 'teatro', 'design'],
    'agrarias': ['agro', 'zootecnia', 'florestal'],
    'humanas': ['direito', 'administração', 'administracao', 'economia', 'pedagogia', 'história', 'historia', 'geografia', 'filosofia', 'sociologia', 'psicologia', 'arquitetura', 'contábeis', 'contabeis', 'jornalismo', 'comunicação', 'comunicacao', 'serviço social', 'servico social', 'relações', 'relacoes']
}

@register.filter(name='cor_categoria')
def cor_categoria(nome_curso):
    """Legado — use category_class para as novas classes cat-*."""
    if not nome_curso:
        return 'border-padrao-curso'
    nome_lower = str(nome_curso).lower()
    for categoria, palavras in PALAVRAS_CHAVE.items():
        if any(palavra in nome_lower for palavra in palavras):
            return f"border-{categoria}"
    return 'border-padrao-curso'

