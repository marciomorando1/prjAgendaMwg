from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Activity, ActivityLog

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username","nome","email","gerente_projetos","is_active","is_staff")
    list_filter = ("gerente_projetos","is_staff","is_active")
    search_fields = ("username","nome","email")

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ("numero","nome_cliente","numero_orcamento","recurso","inicio_previsto","fim_previsto")
    list_filter = ("recurso",)
    search_fields = ("numero_orcamento","nome_cliente","descricao")
    readonly_fields = ("criado_em","atualizado_em")

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ("atividade","usuario","inicio","fim")
    list_filter = ("usuario",)
    search_fields = ("descricao",)
