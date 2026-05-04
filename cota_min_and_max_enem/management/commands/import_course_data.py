import os
import json
from django.core.management.base import BaseCommand
from cota_min_and_max_enem.models import CourseOffering, QuotaData

class Command(BaseCommand):
    help = 'Importa os dados dos cursos em JSON para o banco de dados'

    def add_arguments(self, parser):
        parser.add_argument('--no-delete', action='store_true', help='Não apaga os dados existentes antes de importar')
        parser.add_argument('--source-dir', type=str, help='Diretório específico para importar')
        parser.add_argument('--move', action='store_true', help='Move os arquivos para a estrutura organizada após importar')

    def handle(self, *args, **options):
        no_delete = options.get('no_delete')
        source_dir_arg = options.get('source_dir')
        move_files = options.get('move')

        # Caminho base
        if source_dir_arg:
            base_dir = source_dir_arg
        else:
            base_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
                'pipeline_dados',
                'dados_processados'
            )

        if not os.path.exists(base_dir):
            self.stdout.write(self.style.ERROR(f'O diretório {base_dir} não existe!'))
            return

        self.stdout.write(self.style.SUCCESS(f'Iniciando importação do diretório: {base_dir}'))
        
        if not no_delete:
            self.stdout.write(self.style.WARNING('Apagando dados existentes...'))
            CourseOffering.objects.all().delete()

        arquivos_processados = 0
        ofertas_criadas = 0

        # Para mover arquivos, precisamos da base de destino original
        dest_base = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
            'pipeline_dados',
            'dados_processados'
        )

        for root, _, files in os.walk(base_dir):
            for file in files:
                if file.endswith('.json'):
                    file_path = os.path.join(root, file)
                    if os.name == 'nt':
                        full_path = '\\\\?\\' + os.path.abspath(file_path)
                    else:
                        full_path = file_path

                    try:
                        with open(full_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        institution = data.get("institution")
                        year_reference = data.get("year_reference")
                        
                        if not institution or not year_reference:
                            continue

                        for offering_data in data.get("offerings", []):
                            course_name = offering_data.get("course", "")
                            campus = offering_data.get("campus", "")
                            degree = offering_data.get("degree", "")
                            shift = offering_data.get("shift", "")

                            # Check for existence
                            if CourseOffering.objects.filter(
                                institution=institution,
                                year_reference=year_reference,
                                course_name=course_name,
                                campus=campus,
                                degree=degree,
                                shift=shift
                            ).exists():
                                self.stdout.write(self.style.WARNING(f"Ignorado (já existe): {course_name} - {campus}"))
                                continue

                            course = CourseOffering.objects.create(
                                institution=institution,
                                year_reference=year_reference,
                                course_name=course_name,
                                campus=campus,
                                degree=degree,
                                shift=shift,
                                total_spots_filled=offering_data.get("total_spots_filled", 0),
                                leftover_spots=offering_data.get("leftover_spots", 0)
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
                            
                            if move_files:
                                import shutil
                                shift_slug = shift.strip().lower().replace(" ", "_")
                                target_dir = os.path.join(dest_base, institution.upper(), str(year_reference), shift_slug)
                                os.makedirs(target_dir, exist_ok=True)
                                shutil.move(file_path, os.path.join(target_dir, file))
                                self.stdout.write(f'Importado e movido: {file}')
                        
                        arquivos_processados += 1
                        
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Erro ao processar arquivo {file}: {e}'))

        self.stdout.write(self.style.SUCCESS(f'Importação concluída! Arquivos: {arquivos_processados}. Ofertas: {ofertas_criadas}'))
