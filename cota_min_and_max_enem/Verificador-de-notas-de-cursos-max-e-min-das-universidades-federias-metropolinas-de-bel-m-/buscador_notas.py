import os
import json
import unicodedata
from verificador_cotas import PerfilCandidato, AvaliadorDeCotas

class BuscadorDeNotas:
    def __init__(self, diretorio_base: str):
        self.diretorio_base = diretorio_base

    def _normalizar_texto(self, texto: str) -> str:
        """
        Remove acentos, espaços extras e transforma em minúsculo
        para facilitar a busca.
        Ex: "Engenharia da Computação" -> "engenharia da computacao"
        """
        if not texto: return ""
        texto = texto.strip().lower()
        texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
        return texto

    def buscar_curso_para_perfil(self, nome_curso_desejado: str, perfil: PerfilCandidato) -> list:
        """
        Varre os JSONs, busca o curso, utiliza a cascata de cotas do perfil
        e retorna a nota de corte do melhor enquadramento disponível.
        """
        curso_normalizado = self._normalizar_texto(nome_curso_desejado)
        avaliador = AvaliadorDeCotas(perfil)
        
        resultados = []

        # Percorre recursivamente todas as pastas
        for raiz, _, arquivos in os.walk(self.diretorio_base):
            for arquivo in arquivos:
                if arquivo.endswith(".json"):
                    caminho_completo = os.path.join(raiz, arquivo)
                    
                    try:
                        with open(caminho_completo, 'r', encoding='utf-8') as f:
                            dados = json.load(f)
                    except Exception as e:
                        print(f"Erro ao ler {caminho_completo}: {e}")
                        continue
                    
                    instituicao = dados.get("institution")
                    ano = dados.get("year_reference")
                    
                    if not instituicao: continue
                    
                    # Para esta instituição, gera a ordem de prioridade de cotas (Fallback)
                    cascata_prioridades = avaliador.obter_cascata_de_cotas(instituicao)
                    # Exemplo de cascata: ['ERPCD', 'ERPPI', 'ER', 'EPCD', 'EPPI', 'E', 'AC']
                    
                    for oferta in dados.get("offerings", []):
                        nome_curso_json = self._normalizar_texto(oferta.get("course", ""))
                        
                        if curso_normalizado == nome_curso_json:
                            # Encontramos o curso! Vamos extrair os dados.
                            concorrencia = oferta.get("competition_data", [])
                            
                            # Mapeia as cotas disponíveis no JSON para fácil acesso
                            mapa_cotas_json = { item["quota_code"]: item for item in concorrencia }
                            
                            cota_encontrada = None
                            dados_cota_encontrada = None
                            
                            # Tenta encaixar na melhor cota disponível seguindo a cascata
                            for cota_tentativa in cascata_prioridades:
                                if cota_tentativa in mapa_cotas_json:
                                    cota_encontrada = cota_tentativa
                                    dados_cota_encontrada = mapa_cotas_json[cota_tentativa]
                                    break # Achou a melhor possível, para de descer a cascata!
                                    
                            # Sempre pega a AC para parâmetro de comparação
                            dados_ac = mapa_cotas_json.get("AC", None)
                            # Tratamento para exceções na UEPA ou UFRA (se AC não for a string literal "AC")
                            if not dados_ac and instituicao == "UEPA":
                                dados_ac = mapa_cotas_json.get("Grupo 1 (Código A)")
                            elif not dados_ac and instituicao == "UEPA":
                                # Algumas bases da UEPA podem usar apenas "Grupo 1" ou algo assim
                                dados_ac = mapa_cotas_json.get("Grupo 1")

                            # Se não achou NENHUMA cota (nem AC), pula.
                            if not dados_cota_encontrada:
                                continue
                            
                            resultado_oferta = {
                                "instituicao": instituicao,
                                "campus": oferta.get("campus"),
                                "turno": oferta.get("shift"),
                                "ano_referencia": ano,
                                "cota_perfil": {
                                    "codigo": cota_encontrada,
                                    "descricao": dados_cota_encontrada.get("description", ""),
                                    "nota_minima": dados_cota_encontrada.get("previous_cutoff"),
                                    "nota_maxima": dados_cota_encontrada.get("historical_max_score"),
                                },
                                "ampla_concorrencia": {
                                    "codigo": dados_ac.get("quota_code") if dados_ac else "AC",
                                    "nota_minima": dados_ac.get("previous_cutoff") if dados_ac else None,
                                    "nota_maxima": dados_ac.get("historical_max_score") if dados_ac else None,
                                } if dados_ac else None
                            }
                            resultados.append(resultado_oferta)
                            
        return resultados

if __name__ == "__main__":
    # Teste rápido
    buscador = BuscadorDeNotas("dados_de-cursos")
    
    # Perfil: Pública, Renda Baixa, PPI, PCD
    p_teste = PerfilCandidato(escola_publica=False, renda_sm=1.0, raca='parda', pcd=False)
    
    print("Buscando por 'Engenharia da Computação'...")
    res = buscador.buscar_curso_para_perfil("Engenharia da Computação", p_teste)
    
    print(json.dumps(res, indent=4, ensure_ascii=False))
