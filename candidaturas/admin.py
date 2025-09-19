# candidaturas/admin.py
from django.contrib import admin
from .models import Pais, TipoInstituicao, Instituicao, AreaEstudo, Curso, TipoTaxa, TaxaInscricao, Candidatura, Depoimento

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
    list_display = ['nome', 'instituicao', 'modalidade', 'ativo']
    list_filter = ['modalidade', 'ativo', 'instituicao__pais']
    search_fields = ['nome', 'instituicao__nome']
    autocomplete_fields = ['instituicao', 'area_estudo']
    list_editable = ['ativo']

@admin.register(TipoTaxa)
class TipoTaxaAdmin(admin.ModelAdmin):
    list_display = ['nome']
    search_fields = ['nome']

@admin.register(TaxaInscricao)
class TaxaInscricaoAdmin(admin.ModelAdmin):
    list_display = ['tipo_taxa', 'valor', 'moeda', 'get_associacao', 'ativo']
    list_filter = ['tipo_taxa', 'moeda', 'ativo']
    search_fields = ['curso__nome', 'instituicao__nome', 'pais__nome']
    autocomplete_fields = ['tipo_taxa', 'curso', 'instituicao', 'pais']
    list_editable = ['ativo']
    
    def get_associacao(self, obj):
        if obj.curso:
            return f"Curso: {obj.curso}"
        elif obj.instituicao:
            return f"Instituição: {obj.instituicao}"
        elif obj.pais:
            return f"País: {obj.pais}"
        return "Nenhuma"
    
    get_associacao.short_description = 'Associação'

@admin.register(Candidatura)
class CandidaturaAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nome_completo', 'email', 'curso', 'estado', 'data_submissao']
    list_filter = ['estado', 'data_submissao', 'instituicao__pais']
    search_fields = ['codigo', 'nome_completo', 'email', 'curso__nome']
    readonly_fields = ['codigo', 'data_submissao', 'data_actualizacao']
    autocomplete_fields = ['curso', 'instituicao', 'taxa_inscricao']
    
    def has_add_permission(self, request):
        return True  # Impede adição manual pelo admin