from django.db import models
from django.contrib.auth.models import User

class CourseOffering(models.Model):
    institution = models.CharField(max_length=50)
    year_reference = models.IntegerField()
    course_name = models.CharField(max_length=200)
    campus = models.CharField(max_length=100)
    degree = models.CharField(max_length=100, blank=True, null=True)
    shift = models.CharField(max_length=50)
    total_spots_filled = models.IntegerField(default=0)
    leftover_spots = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.course_name} - {self.institution} ({self.campus})"

class QuotaData(models.Model):
    course_offering = models.ForeignKey(CourseOffering, on_delete=models.CASCADE, related_name="quotas")

    # --- Campos originais ---
    quota_code = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    spots = models.IntegerField(default=0)
    previous_cutoff = models.FloatField(null=True, blank=True)
    historical_max_score = models.FloatField(null=True, blank=True)

    # --- Campo desnormalizado para resolver colisão de códigos entre instituições ---
    # Ex: código "E" significa coisas diferentes na UFPA e na UEPA
    institution = models.CharField(
        max_length=50,
        blank=True,
        default='',
        verbose_name="Instituição",
        help_text="Desnormalizado de course_offering.institution para facilitar filtros diretos."
    )

    # --- Campos booleanos semânticos derivados do quota_code ---
    is_ampla_concorrencia = models.BooleanField(
        default=False,
        verbose_name="Ampla Concorrência",
        help_text="AC (UFPA/IFPA/UFRA) ou A (UEPA). Aberta a todos."
    )
    requer_escola_publica = models.BooleanField(
        default=False,
        verbose_name="Requer Escola Pública",
        help_text="Exige que o candidato tenha cursado o ensino médio integralmente em escola pública."
    )
    requer_renda_baixa = models.BooleanField(
        default=False,
        verbose_name="Requer Renda Baixa (≤ 1 SM)",
        help_text="Exige renda familiar per capita igual ou inferior a 1 salário mínimo."
    )
    is_pcd = models.BooleanField(
        default=False,
        verbose_name="Para PcD",
        help_text="Vaga reservada para Pessoas com Deficiência."
    )
    is_adicional_pcd = models.BooleanField(
        default=False,
        verbose_name="Cota Adicional PcD",
        help_text="Cota adicional exclusiva para PcD independente de escola pública (UFPA: PCDA / UEPA: B)."
    )
    is_ppi = models.BooleanField(
        default=False,
        verbose_name="Para PPI",
        help_text="Vaga reservada para autodeclarados Pretos, Pardos ou Indígenas."
    )
    is_quilombola = models.BooleanField(
        default=False,
        verbose_name="Para Quilombola",
        help_text="Vaga reservada para autodeclarados Quilombolas."
    )

    def __str__(self):
        return f"{self.quota_code} ({self.institution}) - {self.course_offering.course_name}"

class PerfilCandidatoDB(models.Model):
    RACA_CHOICES = [
        ('branca', 'Branca'),
        ('preta', 'Preta'),
        ('parda', 'Parda'),
        ('indigena', 'Indígena'),
        ('quilombola', 'Quilombola'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_candidato')
    escola_publica = models.BooleanField(default=True, verbose_name="Estudou em Escola Pública?")
    renda_sm = models.FloatField(default=1.0, verbose_name="Renda Familiar (em Salários Mínimos por pessoa na residência)")
    raca = models.CharField(max_length=20, choices=RACA_CHOICES, default='branca', verbose_name="Raça/Cor")
    pcd = models.BooleanField(default=False, verbose_name="Pessoa com Deficiência (PCD)?")

    def __str__(self):
        return f"Perfil de {self.user.username}"
