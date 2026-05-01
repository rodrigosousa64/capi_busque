import os
import json
from django.core.management.base import BaseCommand
from cota_min_and_max_enem.models import CourseOffering, QuotaData

class Command(BaseCommand):
    help = 'Importa os dados dos cursos em JSON para o banco de dados'

    def handle(self, *args, **kwargs):
        # Caminho para a nova pasta centralizada de dados
        base_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
            'pipeline_dados',
            'dados_processados'
        )

        if not os.path.exists(base_dir):
            self.stdout.write(self.style.ERROR(f'O diretório {base_dir} não existe!'))
            return

        self.stdout.write(self.style.SUCCESS(f'Iniciando importação do diretório: {base_dir}'))
        
        # Opcional: apagar dados antigos para evitar duplicação em caso de re-execução
        CourseOffering.objects.all().delete()

        arquivos_processados = 0
        ofertas_criadas = 0

        for root, _, files in os.walk(base_dir):
            for file in files:
                if file.endswith('.json'):
                    file_path = os.path.join(root, file)
                    if os.name == 'nt':
                        file_path = '\\\\?\\' + os.path.abspath(file_path)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        institution = data.get("institution")
                        year_reference = data.get("year_reference")
                        
                        if not institution or not year_reference:
                            self.stdout.write(self.style.WARNING(f'Arquivo ignorado (sem instituição/ano): {file_path}'))
                            continue

                        for offering_data in data.get("offerings", []):
                            course = CourseOffering.objects.create(
                                institution=institution,
                                year_reference=year_reference,
                                course_name=offering_data.get("course", ""),
                                campus=offering_data.get("campus", ""),
                                degree=offering_data.get("degree", ""),
                                shift=offering_data.get("shift", ""),
                                total_spots_filled=offering_data.get("total_spots_filled", 0)
                            )
                            ofertas_criadas += 1

                            for quota_data in offering_data.get("competition_data", []):
                                QuotaData.objects.create(
                                    course_offering=course,
                                    quota_code=quota_data.get("quota_code", ""),
                                    description=quota_data.get("description", ""),
                                    spots=quota_data.get("spots", 0),
                                    previous_cutoff=quota_data.get("previous_cutoff"),
                                    historical_max_score=quota_data.get("historical_max_score")
                                )
                        
                        arquivos_processados += 1
                        
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Erro ao processar arquivo {file_path}: {e}'))

        self.stdout.write(self.style.SUCCESS(f'Importação concluída! Arquivos processados: {arquivos_processados}. Ofertas criadas: {ofertas_criadas}'))
