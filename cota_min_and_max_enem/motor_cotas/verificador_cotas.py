from dataclasses import dataclass

@dataclass
class PerfilCandidato:
    escola_publica: bool
    renda_sm: float
    raca: str # 'branca', 'preta', 'parda', 'indigena', 'quilombola'
    pcd: bool

class AvaliadorDeCotas:
    """
    Classe responsável por validar e mapear as cotas universitárias baseadas 
    no perfil do candidato.
    """
    def __init__(self, perfil: PerfilCandidato):
        self.perfil = perfil

    def obter_cota_ifpa(self) -> str:
        """
        1. O Sistema Lógico do IFPA (Escala L1-L8)
        Limite de renda: <= 1.5 SM.
        """
        if not self.perfil.escola_publica:
            return "AC"
        
        eh_ppi = self.perfil.raca in ['preta', 'parda', 'indigena']
        renda_baixa = self.perfil.renda_sm <= 1.5

        if renda_baixa:
            if eh_ppi and not self.perfil.pcd: return "L1"
            if not eh_ppi and not self.perfil.pcd: return "L2"
            if eh_ppi and self.perfil.pcd: return "L5"
            if not eh_ppi and self.perfil.pcd: return "L6"
        else:
            if eh_ppi and not self.perfil.pcd: return "L3"
            if not eh_ppi and not self.perfil.pcd: return "L4"
            if eh_ppi and self.perfil.pcd: return "L7"
            if not eh_ppi and self.perfil.pcd: return "L8"

    def obter_cota_ufpa(self) -> str:
        """
        2. O Sistema Modular da UFPA (Acrônimos)
        Limite de renda: <= 1.5 SM.
        """
        if not self.perfil.escola_publica:
            return "PCDA" if self.perfil.pcd else "AC"
        
        renda_baixa = self.perfil.renda_sm <= 1.0
        eh_ppi = self.perfil.raca in ['preta', 'parda', 'indigena']
        eh_quilombola = self.perfil.raca == 'quilombola'

        if renda_baixa:
            if self.perfil.pcd: return "ERPCD"
            if eh_quilombola: return "ERQ"
            if eh_ppi: return "ERPPI"
            return "ER"
        else:
            if self.perfil.pcd: return "EPCD"
            if eh_quilombola: return "EQ"
            if eh_ppi: return "EPPI"
            return "E"

    def obter_cota_uepa(self) -> str:
        """
        3. A Estrutura de Grupos da UEPA (1 ao 10)
        Acesso Amplo: Grupo 1 (A), Grupo 2 (B - PCD)
        Grupos 3 a 6 (Escola), Grupos 7 a 10 (Escola + Renda <= 1.5)
        """
        if not self.perfil.escola_publica:
            return "B" if self.perfil.pcd else "A"
        
        renda_baixa = self.perfil.renda_sm <= 1.0
        eh_ppi = self.perfil.raca in ['preta', 'parda', 'indigena']
        eh_quilombola = self.perfil.raca == 'quilombola'

        # Retorna apenas a letra do código, que é como o banco de dados armazena
        if self.perfil.pcd and (eh_ppi or eh_quilombola):
            return "J" if renda_baixa else "F"
        elif self.perfil.pcd:
            return "I" if renda_baixa else "E"
        elif eh_ppi or eh_quilombola:
            return "H" if renda_baixa else "D"
        else:
            return "G" if renda_baixa else "C"


    def obter_cota_ufra(self) -> str:
        """
        4. A Lógica SiSU da UFRA (LB vs. LI)
        LB: Baixa Renda <= 1.5 / LI: Livre
        """
        if not self.perfil.escola_publica:
            return "AC"
        
        renda_baixa = self.perfil.renda_sm <= 1.0
        eh_ppi = self.perfil.raca in ['preta', 'parda', 'indigena']
        eh_quilombola = self.perfil.raca == 'quilombola'

        prefix = "LB" if renda_baixa else "LI"

        if eh_quilombola:
            return f"{prefix}_Q"
        elif eh_ppi:
            return f"{prefix}_PPI"
        elif self.perfil.pcd:
            return f"{prefix}_PCD"
        else:
            return f"{prefix}_EP"

    def identificar_cotas(self) -> dict:
        """
        Retorna a cota específica do perfil para cada universidade e também
        a cota de Ampla Concorrência, pois o aluno sempre pode concorrer nela.
        """
        return {
            "IFPA": {
                "cota_especifica": self.obter_cota_ifpa(),
                "ampla_concorrencia": "AC"
            },
            "UFPA": {
                "cota_especifica": self.obter_cota_ufpa(),
                "ampla_concorrencia": "AC"
            },
            "UEPA": {
                "cota_especifica": self.obter_cota_uepa(),
                "ampla_concorrencia": "A"
            },
            "UFRA": {
                "cota_especifica": self.obter_cota_ufra(),
                "ampla_concorrencia": "AC"
            }
        }

    def obter_cascata_de_cotas(self, faculdade: str) -> list[str]:
        """
        Gera uma lista ordenada de cotas válidas para o candidato (Fallback),
        da mais restrita/específica até a Ampla Concorrência.
        """
        cotas_validas = []
        p_atual = self.perfil

        def add_cota(p_temp):
            aval_temp = AvaliadorDeCotas(p_temp)
            if faculdade == "IFPA": sigla = aval_temp.obter_cota_ifpa()
            elif faculdade == "UFPA": sigla = aval_temp.obter_cota_ufpa()
            elif faculdade == "UEPA": sigla = aval_temp.obter_cota_uepa()
            elif faculdade == "UFRA": sigla = aval_temp.obter_cota_ufra()
            else: return
            
            if sigla not in cotas_validas:
                cotas_validas.append(sigla)

        # 1. Cota exata
        add_cota(p_atual)

        # 2. Relaxa PCD
        if p_atual.pcd:
            add_cota(PerfilCandidato(p_atual.escola_publica, p_atual.renda_sm, p_atual.raca, False))

        # 3. Relaxa Etnia
        if p_atual.raca != 'branca':
            add_cota(PerfilCandidato(p_atual.escola_publica, p_atual.renda_sm, 'branca', p_atual.pcd))
            if p_atual.pcd:
                add_cota(PerfilCandidato(p_atual.escola_publica, p_atual.renda_sm, 'branca', False))

        # 4. Relaxa Renda
        if p_atual.renda_sm <= 1.5:
            add_cota(PerfilCandidato(p_atual.escola_publica, 5.0, p_atual.raca, p_atual.pcd))
            if p_atual.pcd:
                add_cota(PerfilCandidato(p_atual.escola_publica, 5.0, p_atual.raca, False))
            if p_atual.raca != 'branca':
                add_cota(PerfilCandidato(p_atual.escola_publica, 5.0, 'branca', p_atual.pcd))
                if p_atual.pcd:
                    add_cota(PerfilCandidato(p_atual.escola_publica, 5.0, 'branca', False))

        # 5. Ampla Concorrência (Fallback final absoluto)
        add_cota(PerfilCandidato(False, 5.0, 'branca', False))

        return cotas_validas


if __name__ == "__main__":
    # Teste 1: Estudante de escola pública, baixa renda, PPI, sem deficiência
    p1 = PerfilCandidato(escola_publica=True, renda_sm=1.0, raca='parda', pcd=False)
    avaliador1 = AvaliadorDeCotas(p1)

    print("--- Perfil 1: Escola Pública, Renda <= 1.5, Parda, Sem PCD ---")
    resultado_p1 = avaliador1.identificar_cotas()
    
    for faculdade, cotas in resultado_p1.items():
        print(f"{faculdade}: Cota Principal -> {cotas['cota_especifica']} | Ampla -> {cotas['ampla_concorrencia']}")
    
    print("\n--- Perfil 2: Escola Privada, Renda Alta, Branca, Sem PCD ---")
    p2 = PerfilCandidato(escola_publica=False, renda_sm=5.0, raca='branca', pcd=False)
    avaliador2 = AvaliadorDeCotas(p2)
    resultado_p2 = avaliador2.identificar_cotas()
    for faculdade, cotas in resultado_p2.items():
        print(f"{faculdade}: Cota Principal -> {cotas['cota_especifica']} | Ampla -> {cotas['ampla_concorrencia']}")

    print("\n--- Perfil 3: Escola Pública, Renda > 1.5, Quilombola, Com PCD ---")
    p3 = PerfilCandidato(escola_publica=True, renda_sm=2.0, raca='quilombola', pcd=True)
    avaliador3 = AvaliadorDeCotas(p3)
    resultado_p3 = avaliador3.identificar_cotas()
    for faculdade, cotas in resultado_p3.items():
        print(f"{faculdade}: Cota Principal -> {cotas['cota_especifica']} | Ampla -> {cotas['ampla_concorrencia']}")
