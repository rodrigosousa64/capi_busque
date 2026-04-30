from django.contrib import admin
from .models import CourseOffering, QuotaData, PerfilCandidatoDB

@admin.register(CourseOffering)
class CourseOfferingAdmin(admin.ModelAdmin):
    list_display = ('course_name', 'institution', 'campus', 'shift', 'year_reference')
    list_filter = ('institution', 'campus', 'shift', 'year_reference')
    search_fields = ('course_name', 'institution', 'campus')

@admin.register(QuotaData)
class QuotaDataAdmin(admin.ModelAdmin):
    list_display = ('course_offering', 'quota_code', 'previous_cutoff', 'historical_max_score')
    list_filter = ('quota_code',)
    search_fields = ('course_offering__course_name', 'quota_code', 'description')

@admin.register(PerfilCandidatoDB)
class PerfilCandidatoDBAdmin(admin.ModelAdmin):
    list_display = ('user', 'escola_publica', 'renda_sm', 'raca', 'pcd')
    list_filter = ('escola_publica', 'raca', 'pcd')
    search_fields = ('user__username', 'user__email')
