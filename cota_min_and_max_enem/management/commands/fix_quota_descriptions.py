from django.core.management.base import BaseCommand
from cota_min_and_max_enem.models import QuotaData


DESCRICOES_CORRETAS = {
    # UEPA
    "A": "Ampla Concorrência (Grupo 1)",
    "B": "Cota Adicional Exclusiva para Pessoas com Deficiência - PcD (Grupo 2)",
    "C": "Cota Escola (Grupo 3)",
    "D": "Cota Escola + PcD (Grupo 4)",
    "E": "Cota Escola + Étnico-Racial-Quilombola (Grupo 5)",
    "F": "Cota Escola + Étnico-Racial-Quilombola + PcD (Grupo 6)",
    "G": "Cota Escola + Renda (Grupo 7)",
    "H": "Cota Escola + Renda + PcD (Grupo 8)",
    "I": "Cota Escola + Renda + Étnico-Racial-Quilombola (Grupo 9)",
    "J": "Cota Escola + Renda + Étnico-Racial-Quilombola + PcD (Grupo 10)",

    # IFPA
    "AC":  "Ampla Concorrência",
    "L1":  "Escola Pública + Renda ≤ 1,5 SM + Autodeclarados Pretos, Pardos ou Indígenas (PPI)",
    "L2":  "Escola Pública + Renda ≤ 1,5 SM",
    "L3":  "Escola Pública + Renda > 1,5 SM + Autodeclarados Pretos, Pardos ou Indígenas (PPI)",
    "L4":  "Escola Pública + Renda > 1,5 SM",
    "L5":  "Escola Pública + Renda ≤ 1,5 SM + PPI + Pessoas com Deficiência (PcD)",
    "L6":  "Escola Pública + Renda ≤ 1,5 SM + Pessoas com Deficiência (PcD)",
    "L7":  "Escola Pública + Renda > 1,5 SM + PPI + Pessoas com Deficiência (PcD)",
    "L8":  "Escola Pública + Renda > 1,5 SM + Pessoas com Deficiência (PcD)",

    # UFPA
    "PCDA":  "Cota Adicional Exclusiva para Pessoas com Deficiência (independente da origem escolar)",
    "E":     "Apenas Cota Escola",
    "EPCD":  "Cota Escola + Pessoas com Deficiência (PcD)",
    "EQ":    "Cota Escola + Quilombolas",
    "EPPI":  "Cota Escola + Autodeclarados Pretos, Pardos ou Indígenas (PPI)",
    "ER":    "Cota Escola + Renda familiar per capita ≤ 1 salário mínimo",
    "ERPCD": "Cota Escola + Renda ≤ 1 SM + Pessoas com Deficiência (PcD)",
    "ERQ":   "Cota Escola + Renda ≤ 1 SM + Quilombolas",
    "ERPPI": "Cota Escola + Renda ≤ 1 SM + Autodeclarados Pretos, Pardos ou Indígenas (PPI)",

    # UFRA
    "LB_EP":  "Cota Escola + Renda ≤ 1 SM. Sem critério de raça ou deficiência",
    "LB_PPI": "Cota Escola + Renda ≤ 1 SM + Autodeclarados Pretos, Pardos ou Indígenas (PPI)",
    "LB_Q":   "Cota Escola + Renda ≤ 1 SM + Quilombolas",
    "LB_PCD": "Cota Escola + Renda ≤ 1 SM + Pessoas com Deficiência (PcD)",
    "LI_EP":  "Cota Escola + Renda Livre. Sem critério de raça ou deficiência",
    "LI_PPI": "Cota Escola + Renda Livre + Autodeclarados Pretos, Pardos ou Indígenas (PPI)",
    "LI_PCD": "Cota Escola + Renda Livre + Pessoas com Deficiência (PcD)",
}


class Command(BaseCommand):
    help = 'Atualiza as descrições das cotas no banco de dados com os textos oficiais corretos'

    def handle(self, *args, **kwargs):
        atualizados = 0
        nao_encontrados = set()

        for codigo, descricao_correta in DESCRICOES_CORRETAS.items():
            quantidade = QuotaData.objects.filter(quota_code=codigo).update(description=descricao_correta)
            if quantidade > 0:
                atualizados += quantidade
                self.stdout.write(self.style.SUCCESS(f'  [{codigo}] -> {quantidade} registro(s) atualizado(s)'))
            else:
                nao_encontrados.add(codigo)

        self.stdout.write(self.style.SUCCESS(f'\n✅ Total atualizado: {atualizados} registro(s).'))

        if nao_encontrados:
            self.stdout.write(self.style.WARNING(f'⚠️  Códigos não encontrados no banco (sem registros): {", ".join(sorted(nao_encontrados))}'))
