"""
Data Migration 0006 — Popula campos booleanos semânticos no QuotaData.

Lê o 'quota_code' + 'institution' de cada registro existente e define:
    - institution (desnormalizado de course_offering.institution)
    - is_ampla_concorrencia
    - requer_escola_publica
    - requer_renda_baixa
    - is_pcd
    - is_adicional_pcd
    - is_ppi
    - is_quilombola

Tabela de referência completa por instituição:
    UFPA  → AC, PCDA, E, EPCD, EQ, EPPI, ER, ERPCD, ERQ, ERPPI
    IFPA  → AC, RI_PPI, RI_Q, RI_PCD, RI_EP, IR_PPI, IR_Q, IR_PCD, IR_EP
    UEPA  → A, B, C, D, E, F, G, H, I, J
    UFRA  → AC, LB_EP, LB_PPI, LB_Q, LB_PCD, LI_EP, LI_PPI, LI_PCD
"""

from django.db import migrations

# ---------------------------------------------------------------------------
# Mapa de flags: (institution, quota_code) -> dict de campos booleanos
# ---------------------------------------------------------------------------
# Estrutura de cada entry:
#   is_ampla_concorrencia  → True se for AC / A (ampla concorrência)
#   requer_escola_publica  → True se exige ensino médio em escola pública
#   requer_renda_baixa     → True se exige renda ≤ 1 SM per capita
#   is_ppi                 → True para Pretos, Pardos ou Indígenas
#   is_quilombola          → True para Quilombolas
#   is_pcd                 → True para Pessoas com Deficiência
#   is_adicional_pcd       → True quando é cota adicional PcD (independente de escola)
# ---------------------------------------------------------------------------
QUOTA_MAP = {
    # ─── UFPA — Sistema Modular ─────────────────────────────────────────────
    ("UFPA", "AC"):     dict(is_ampla_concorrencia=True,  requer_escola_publica=False, requer_renda_baixa=False, is_ppi=False, is_quilombola=False, is_pcd=False, is_adicional_pcd=False),
    ("UFPA", "PCDA"):   dict(is_ampla_concorrencia=False, requer_escola_publica=False, requer_renda_baixa=False, is_ppi=False, is_quilombola=False, is_pcd=True,  is_adicional_pcd=True),
    ("UFPA", "E"):      dict(is_ampla_concorrencia=False, requer_escola_publica=True,  requer_renda_baixa=False, is_ppi=False, is_quilombola=False, is_pcd=False, is_adicional_pcd=False),
    ("UFPA", "EPCD"):   dict(is_ampla_concorrencia=False, requer_escola_publica=True,  requer_renda_baixa=False, is_ppi=False, is_quilombola=False, is_pcd=True,  is_adicional_pcd=False),
    ("UFPA", "EQ"):     dict(is_ampla_concorrencia=False, requer_escola_publica=True,  requer_renda_baixa=False, is_ppi=False, is_quilombola=True,  is_pcd=False, is_adicional_pcd=False),
    ("UFPA", "EPPI"):   dict(is_ampla_concorrencia=False, requer_escola_publica=True,  requer_renda_baixa=False, is_ppi=True,  is_quilombola=False, is_pcd=False, is_adicional_pcd=False),
    ("UFPA", "ER"):     dict(is_ampla_concorrencia=False, requer_escola_publica=True,  requer_renda_baixa=True,  is_ppi=False, is_quilombola=False, is_pcd=False, is_adicional_pcd=False),
    ("UFPA", "ERPCD"):  dict(is_ampla_concorrencia=False, requer_escola_publica=True,  requer_renda_baixa=True,  is_ppi=False, is_quilombola=False, is_pcd=True,  is_adicional_pcd=False),
    ("UFPA", "ERQ"):    dict(is_ampla_concorrencia=False, requer_escola_publica=True,  requer_renda_baixa=True,  is_ppi=False, is_quilombola=True,  is_pcd=False, is_adicional_pcd=False),
    ("UFPA", "ERPPI"):  dict(is_ampla_concorrencia=False, requer_escola_publica=True,  requer_renda_baixa=True,  is_ppi=True,  is_quilombola=False, is_pcd=False, is_adicional_pcd=False),

    # ─── IFPA — Novo Sistema PSU 2026 ───────────────────────────────────────
    ("IFPA", "AC"):     dict(is_ampla_concorrencia=True,  requer_escola_publica=False, requer_renda_baixa=False, is_ppi=False, is_quilombola=False, is_pcd=False, is_adicional_pcd=False),
    ("IFPA", "RI_PPI"): dict(is_ampla_concorrencia=False, requer_escola_publica=True,  requer_renda_baixa=True,  is_ppi=True,  is_quilombola=False, is_pcd=False, is_adicional_pcd=False),
    ("IFPA", "RI_Q"):   dict(is_ampla_concorrencia=False, requer_escola_publica=True,  requer_renda_baixa=True,  is_ppi=False, is_quilombola=True,  is_pcd=False, is_adicional_pcd=False),
    ("IFPA", "RI_PCD"): dict(is_ampla_concorrencia=False, requer_escola_publica=True,  requer_renda_baixa=True,  is_ppi=False, is_quilombola=False, is_pcd=True,  is_adicional_pcd=False),
    ("IFPA", "RI_EP"):  dict(is_ampla_concorrencia=False, requer_escola_publica=True,  requer_renda_baixa=True,  is_ppi=False, is_quilombola=False, is_pcd=False, is_adicional_pcd=False),
    ("IFPA", "IR_PPI"): dict(is_ampla_concorrencia=False, requer_escola_publica=True,  requer_renda_baixa=False, is_ppi=True,  is_quilombola=False, is_pcd=False, is_adicional_pcd=False),
    ("IFPA", "IR_Q"):   dict(is_ampla_concorrencia=False, requer_escola_publica=True,  requer_renda_baixa=False, is_ppi=False, is_quilombola=True,  is_pcd=False, is_adicional_pcd=False),
    ("IFPA", "IR_PCD"): dict(is_ampla_concorrencia=False, requer_escola_publica=True,  requer_renda_baixa=False, is_ppi=False, is_quilombola=False, is_pcd=True,  is_adicional_pcd=False),
    ("IFPA", "IR_EP"):  dict(is_ampla_concorrencia=False, requer_escola_publica=True,  requer_renda_baixa=False, is_ppi=False, is_quilombola=False, is_pcd=False, is_adicional_pcd=False),

    # ─── UEPA — Estrutura de Grupos A–J ─────────────────────────────────────
    # Grupos E, F, I, J: is_ppi=True E is_quilombola=True ao mesmo tempo,
    # pois a UEPA unifica "Étnico-Racial-Quilombola" num único grupo.
    ("UEPA", "A"):  dict(is_ampla_concorrencia=True,  requer_escola_publica=False, requer_renda_baixa=False, is_ppi=False, is_quilombola=False, is_pcd=False, is_adicional_pcd=False),
    ("UEPA", "B"):  dict(is_ampla_concorrencia=False, requer_escola_publica=False, requer_renda_baixa=False, is_ppi=False, is_quilombola=False, is_pcd=True,  is_adicional_pcd=True),
    ("UEPA", "C"):  dict(is_ampla_concorrencia=False, requer_escola_publica=True,  requer_renda_baixa=False, is_ppi=False, is_quilombola=False, is_pcd=False, is_adicional_pcd=False),
    ("UEPA", "D"):  dict(is_ampla_concorrencia=False, requer_escola_publica=True,  requer_renda_baixa=False, is_ppi=False, is_quilombola=False, is_pcd=True,  is_adicional_pcd=False),
    ("UEPA", "E"):  dict(is_ampla_concorrencia=False, requer_escola_publica=True,  requer_renda_baixa=False, is_ppi=True,  is_quilombola=True,  is_pcd=False, is_adicional_pcd=False),
    ("UEPA", "F"):  dict(is_ampla_concorrencia=False, requer_escola_publica=True,  requer_renda_baixa=False, is_ppi=True,  is_quilombola=True,  is_pcd=True,  is_adicional_pcd=False),
    ("UEPA", "G"):  dict(is_ampla_concorrencia=False, requer_escola_publica=True,  requer_renda_baixa=True,  is_ppi=False, is_quilombola=False, is_pcd=False, is_adicional_pcd=False),
    ("UEPA", "H"):  dict(is_ampla_concorrencia=False, requer_escola_publica=True,  requer_renda_baixa=True,  is_ppi=False, is_quilombola=False, is_pcd=True,  is_adicional_pcd=False),
    ("UEPA", "I"):  dict(is_ampla_concorrencia=False, requer_escola_publica=True,  requer_renda_baixa=True,  is_ppi=True,  is_quilombola=True,  is_pcd=False, is_adicional_pcd=False),
    ("UEPA", "J"):  dict(is_ampla_concorrencia=False, requer_escola_publica=True,  requer_renda_baixa=True,  is_ppi=True,  is_quilombola=True,  is_pcd=True,  is_adicional_pcd=False),

    # ─── UFRA — Lógica SiSU (LB vs LI) ─────────────────────────────────────
    ("UFRA", "AC"):     dict(is_ampla_concorrencia=True,  requer_escola_publica=False, requer_renda_baixa=False, is_ppi=False, is_quilombola=False, is_pcd=False, is_adicional_pcd=False),
    ("UFRA", "LB_EP"):  dict(is_ampla_concorrencia=False, requer_escola_publica=True,  requer_renda_baixa=True,  is_ppi=False, is_quilombola=False, is_pcd=False, is_adicional_pcd=False),
    ("UFRA", "LB_PPI"): dict(is_ampla_concorrencia=False, requer_escola_publica=True,  requer_renda_baixa=True,  is_ppi=True,  is_quilombola=False, is_pcd=False, is_adicional_pcd=False),
    ("UFRA", "LB_Q"):   dict(is_ampla_concorrencia=False, requer_escola_publica=True,  requer_renda_baixa=True,  is_ppi=False, is_quilombola=True,  is_pcd=False, is_adicional_pcd=False),
    ("UFRA", "LB_PCD"): dict(is_ampla_concorrencia=False, requer_escola_publica=True,  requer_renda_baixa=True,  is_ppi=False, is_quilombola=False, is_pcd=True,  is_adicional_pcd=False),
    ("UFRA", "LI_EP"):  dict(is_ampla_concorrencia=False, requer_escola_publica=True,  requer_renda_baixa=False, is_ppi=False, is_quilombola=False, is_pcd=False, is_adicional_pcd=False),
    ("UFRA", "LI_PPI"): dict(is_ampla_concorrencia=False, requer_escola_publica=True,  requer_renda_baixa=False, is_ppi=True,  is_quilombola=False, is_pcd=False, is_adicional_pcd=False),
    ("UFRA", "LI_PCD"): dict(is_ampla_concorrencia=False, requer_escola_publica=True,  requer_renda_baixa=False, is_ppi=False, is_quilombola=False, is_pcd=True,  is_adicional_pcd=False),
}

BOOLEAN_FIELDS = [
    'institution',
    'is_ampla_concorrencia',
    'requer_escola_publica',
    'requer_renda_baixa',
    'is_pcd',
    'is_adicional_pcd',
    'is_ppi',
    'is_quilombola',
]


def populate_boolean_fields(apps, schema_editor):
    """
    Itera todos os QuotaData existentes e preenche os campos booleanos
    a partir do quota_code + institution do CourseOffering relacionado.

    Usa bulk_update em lotes de 500 para performance em bancos grandes.
    Códigos não reconhecidos são logados, mas não bloqueiam a migração —
    eles ficam com institution preenchido e booleanos em False.
    """
    QuotaData = apps.get_model('cota_min_and_max_enem', 'QuotaData')

    to_update = []
    skipped = []

    for quota in QuotaData.objects.select_related('course_offering').iterator():
        inst = quota.course_offering.institution
        code = quota.quota_code.strip()

        # Preenche institution em todos os casos
        quota.institution = inst

        flags = QUOTA_MAP.get((inst, code))

        if flags is None:
            # Código desconhecido: mantém booleanos em False e registra aviso
            skipped.append(f"  [{inst}] código não mapeado: '{code}' (id={quota.id})")
        else:
            quota.is_ampla_concorrencia  = flags['is_ampla_concorrencia']
            quota.requer_escola_publica  = flags['requer_escola_publica']
            quota.requer_renda_baixa     = flags['requer_renda_baixa']
            quota.is_pcd                 = flags['is_pcd']
            quota.is_adicional_pcd       = flags['is_adicional_pcd']
            quota.is_ppi                 = flags['is_ppi']
            quota.is_quilombola          = flags['is_quilombola']

        to_update.append(quota)

    # Salva tudo em lote
    if to_update:
        QuotaData.objects.bulk_update(to_update, BOOLEAN_FIELDS, batch_size=500)

    # Relatório final
    total = len(to_update)
    total_ok = total - len(skipped)
    print(f"\n[OK] {total_ok}/{total} registros populados com sucesso.")
    if skipped:
        print(f"[AVISO] {len(skipped)} código(s) não reconhecido(s) — verifique se precisa adicionar ao QUOTA_MAP:")
        for s in skipped:
            print(s)


def reverse_populate(apps, schema_editor):
    """Reverte: reseta todos os campos booleanos para False/vazio."""
    QuotaData = apps.get_model('cota_min_and_max_enem', 'QuotaData')
    QuotaData.objects.all().update(
        institution='',
        is_ampla_concorrencia=False,
        requer_escola_publica=False,
        requer_renda_baixa=False,
        is_pcd=False,
        is_adicional_pcd=False,
        is_ppi=False,
        is_quilombola=False,
    )


class Migration(migrations.Migration):

    dependencies = [
        # Depende da migração 0005 que criou os campos no schema
        ('cota_min_and_max_enem', '0005_quotadata_add_boolean_fields'),
    ]

    operations = [
        migrations.RunPython(populate_boolean_fields, reverse_code=reverse_populate),
    ]
