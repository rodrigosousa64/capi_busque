from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cota_min_and_max_enem', '0004_alter_courseoffering_id_alter_perfilcandidatodb_id_and_more'),
    ]

    operations = [
        # Campo desnormalizado de instituição (para resolver colisão de códigos entre UFPA e UEPA)
        migrations.AddField(
            model_name='quotadata',
            name='institution',
            field=models.CharField(
                blank=True,
                default='',
                help_text='Desnormalizado de course_offering.institution para facilitar filtros diretos.',
                max_length=50,
                verbose_name='Instituição',
            ),
        ),
        # Ampla Concorrência
        migrations.AddField(
            model_name='quotadata',
            name='is_ampla_concorrencia',
            field=models.BooleanField(
                default=False,
                help_text='AC (UFPA/IFPA/UFRA) ou A (UEPA). Aberta a todos.',
                verbose_name='Ampla Concorrência',
            ),
        ),
        # Escola Pública
        migrations.AddField(
            model_name='quotadata',
            name='requer_escola_publica',
            field=models.BooleanField(
                default=False,
                help_text='Exige que o candidato tenha cursado o ensino médio integralmente em escola pública.',
                verbose_name='Requer Escola Pública',
            ),
        ),
        # Renda Baixa
        migrations.AddField(
            model_name='quotadata',
            name='requer_renda_baixa',
            field=models.BooleanField(
                default=False,
                help_text='Exige renda familiar per capita igual ou inferior a 1 salário mínimo.',
                verbose_name='Requer Renda Baixa (≤ 1 SM)',
            ),
        ),
        # PcD
        migrations.AddField(
            model_name='quotadata',
            name='is_pcd',
            field=models.BooleanField(
                default=False,
                help_text='Vaga reservada para Pessoas com Deficiência.',
                verbose_name='Para PcD',
            ),
        ),
        # Cota Adicional PcD (independente de escola pública)
        migrations.AddField(
            model_name='quotadata',
            name='is_adicional_pcd',
            field=models.BooleanField(
                default=False,
                help_text='Cota adicional exclusiva para PcD independente de escola pública (UFPA: PCDA / UEPA: B).',
                verbose_name='Cota Adicional PcD',
            ),
        ),
        # PPI
        migrations.AddField(
            model_name='quotadata',
            name='is_ppi',
            field=models.BooleanField(
                default=False,
                help_text='Vaga reservada para autodeclarados Pretos, Pardos ou Indígenas.',
                verbose_name='Para PPI',
            ),
        ),
        # Quilombola
        migrations.AddField(
            model_name='quotadata',
            name='is_quilombola',
            field=models.BooleanField(
                default=False,
                help_text='Vaga reservada para autodeclarados Quilombolas.',
                verbose_name='Para Quilombola',
            ),
        ),
    ]
