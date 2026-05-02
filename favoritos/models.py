from django.db import models
from django.contrib.auth.models import User
from cota_min_and_max_enem.models import CourseOffering

class Favorito(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favoritos')
    oferta = models.ForeignKey(CourseOffering, on_delete=models.CASCADE, related_name='favoritado_por')
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'oferta')

    def __str__(self):
        return f"{self.user.username} favoritou {self.oferta.course_name}"
