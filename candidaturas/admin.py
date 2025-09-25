from django.contrib import admin
from .models import Pais, TipoInstituicao, Instituicao, AreaEstudo, Curso, Candidatura, Depoimento

@admin.register(Pais)
class PaisAdmin(admin.ModelAdmin):
    list_display = ['nome', 'codigo', 'ativo']
    list_filter = ['ativo']
    search_fields = ['nome', 'codigo']
    list_editable = ['ativo']

@admin.register(TipoInstituicao)
class TipoInstituicaoAdmin(admin.ModelAdmin):
    list_display = ['nome']
    search_fields = ['nome']

@admin.register(Instituicao)
class InstituicaoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'pais', 'tipo', 'premium', 'ativo']
    list_filter = ['pais', 'tipo', 'premium', 'ativo']
    search_fields = ['nome']
    autocomplete_fields = ['pais', 'tipo']
    list_editable = ['ativo', 'premium']

@admin.register(AreaEstudo)
class AreaEstudoAdmin(admin.ModelAdmin):
    list_display = ['nome']
    search_fields = ['nome']

@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'instituicao', 'tipo', 'modalidade', 'preco', 'ativo']
    list_filter = ['modalidade', 'tipo', 'ativo', 'instituicao__pais']
    search_fields = ['nome', 'instituicao__nome']
    autocomplete_fields = ['instituicao', 'area_estudo']
    list_editable = ['ativo']

@admin.register(Candidatura)
class CandidaturaAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nome_completo', 'email', 'curso', 'estado', 'data_submissao']
    list_filter = ['estado', 'data_submissao', 'instituicao__pais']
    search_fields = ['codigo', 'nome_completo', 'email', 'curso__nome']
    readonly_fields = ['codigo', 'data_submissao', 'data_actualizacao']
    autocomplete_fields = ['curso', 'instituicao']

@admin.register(Depoimento)
class DepoimentoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'curso', 'instituicao', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['nome', 'texto']
    autocomplete_fields = ['curso', 'instituicao']