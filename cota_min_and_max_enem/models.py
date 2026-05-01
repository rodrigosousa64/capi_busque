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
    quota_code = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    spots = models.IntegerField(default=0)
    previous_cutoff = models.FloatField(null=True, blank=True)
    historical_max_score = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.quota_code} - {self.course_offering.course_name}"

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
