import os
import sys
import json
import unicodedata
from verificador_cotas import PerfilCandidato, AvaliadorDeCotas

# Setup Django context if run as a script
if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.append(project_root)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    import django
    django.setup()

from cota_min_and_max_enem.models import CourseOffering, QuotaData

class BuscadorDeNotas:
    def __init__(self, diretorio_base: str = None):
        # diretorio_base mantido para compatibilidade, mas não será mais usado
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
        Busca o curso no banco de dados, utiliza a cascata de cotas do perfil
        e retorna a nota de corte do melhor enquadramento disponível.
        """
        curso_normalizado = self._normalizar_texto(nome_curso_desejado)
        avaliador = AvaliadorDeCotas(perfil)
        
        resultados = []

        # Busca todas as ofertas e quotas de uma vez para otimizar
        # (Idealmente, usaríamos unaccent no banco, mas SQLite não suporta nativamente)
        todas_ofertas = CourseOffering.objects.prefetch_related('quotas').all()

        for oferta in todas_ofertas:
            nome_curso_db = self._normalizar_texto(oferta.course_name)
            
            # Se a palavra-chave buscada estiver contida no nome do curso
            if curso_normalizado in nome_curso_db:
                instituicao = oferta.institution
                
                # Gera a ordem de prioridade de cotas (Fallback)
                cascata_prioridades = avaliador.obter_cascata_de_cotas(instituicao)
                
                # Mapeia as cotas disponíveis no banco para esta oferta
                mapa_cotas_db = {q.quota_code: q for q in oferta.quotas.all()}
                todas_cotas_do_perfil = []
                # Coleta todas as cotas válidas para o perfil na oferta atual
                for cota_tentativa in cascata_prioridades:
                    if cota_tentativa in mapa_cotas_db:
                        todas_cotas_do_perfil.append(mapa_cotas_db[cota_tentativa])
                
                # Sempre pega a AC para parâmetro de comparação
                dados_ac = mapa_cotas_db.get("AC", None)
                if not dados_ac and instituicao == "UEPA":
                    dados_ac = mapa_cotas_db.get("A")

                # Se não achou NENHUMA cota, pula.
                if not todas_cotas_do_perfil:
                    continue
                    
                # Ordena as cotas pela menor nota de corte
                def sort_key(q):
                    return q.previous_cutoff if q.previous_cutoff is not None else float('inf')
                
                todas_cotas_do_perfil.sort(key=sort_key)
                
                dados_cota_encontrada = todas_cotas_do_perfil[0]
                cota_encontrada = dados_cota_encontrada.quota_code
                
                outras_cotas_validas = []
                for q in todas_cotas_do_perfil[1:]:
                    if q.quota_code not in ["AC", "A"]:
                        outras_cotas_validas.append({
                            "codigo": q.quota_code,
                            "descricao": q.description,
                            "vagas": q.spots,
                            "nota_minima": q.previous_cutoff,
                            "nota_maxima": q.historical_max_score,
                        })
                
                resultado_oferta = {
                    "instituicao": instituicao,
                    "nome_curso": oferta.course_name,
                    "campus": oferta.campus,
                    "turno": oferta.shift,
                    "ano_referencia": oferta.year_reference,
                    "total_vagas": oferta.total_spots_filled,
                    "cota_perfil": {
                        "codigo": cota_encontrada,
                        "descricao": dados_cota_encontrada.description,
                        "vagas": dados_cota_encontrada.spots,
                        "nota_minima": dados_cota_encontrada.previous_cutoff,
                        "nota_maxima": dados_cota_encontrada.historical_max_score,
                    },
                    "outras_cotas": outras_cotas_validas,
                    "ampla_concorrencia": {
                        "codigo": dados_ac.quota_code if dados_ac else "AC",
                        "vagas": dados_ac.spots if dados_ac else None,
                        "nota_minima": dados_ac.previous_cutoff if dados_ac else None,
                        "nota_maxima": dados_ac.historical_max_score if dados_ac else None,
                    } if dados_ac else None
                }
                resultados.append(resultado_oferta)
                            
        return resultados

if __name__ == "__main__":
    # Teste rápido
    buscador = BuscadorDeNotas()
    
    # Perfil: Privada, Renda Baixa, Parda, Sem PCD
    p_teste = PerfilCandidato(escola_publica=False, renda_sm=1.0, raca='parda', pcd=False)
    
    # Na importação, vimos que tem cursos de "Tecnologia Em Análise E Desenvolvimento De Sistemas"
    curso_teste = "tecnologia em analise e desenvolvimento de sistemas"
    print(f"Buscando por '{curso_teste}'...")
    res = buscador.buscar_curso_para_perfil(curso_teste, p_teste)
    
    print(json.dumps(res, indent=4, ensure_ascii=False))
