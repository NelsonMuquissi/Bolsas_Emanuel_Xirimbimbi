# candidaturas/models.py
from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

class Pais(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    codigo = models.CharField(max_length=3, unique=True)
    ativo = models.BooleanField(default=True)
    
    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "País"
        verbose_name_plural = "Países"


class TipoInstituicao(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True)
    
    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Tipo de Instituição"
        verbose_name_plural = "Tipos de Instituição"


class Instituicao(models.Model):
    nome = models.CharField(max_length=255)
    pais = models.ForeignKey(Pais, on_delete=models.PROTECT)
    tipo = models.ForeignKey(TipoInstituicao, on_delete=models.PROTECT)
    ativo = models.BooleanField(default=True)
    premium = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.nome} ({self.pais})"

    class Meta:
        verbose_name = "Instituição"
        verbose_name_plural = "Instituições"
        unique_together = ['nome', 'pais']


class AreaEstudo(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True)
    
    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Área de Estudo"
        verbose_name_plural = "Áreas de Estudo"


class Curso(models.Model):
    MODALIDADE_CHOICES = [
        ('presencial', 'Presencial'),
        ('virtual', 'Virtual'),
        ('hibrido', 'Híbrido'),
    ]
    
    nome = models.CharField(max_length=255)
    instituicao = models.ForeignKey(Instituicao, on_delete=models.CASCADE)
    area_estudo = models.ForeignKey(AreaEstudo, on_delete=models.SET_NULL, null=True, blank=True)
    modalidade = models.CharField(max_length=20, choices=MODALIDADE_CHOICES, default='presencial')
    duracao = models.PositiveIntegerField(help_text="Duração em semestres", null=True, blank=True)
    ativo = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.nome} - {self.instituicao}"

    class Meta:
        verbose_name = "Curso"
        verbose_name_plural = "Cursos"
        unique_together = ['nome', 'instituicao']


class TipoTaxa(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True)
    
    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Tipo de Taxa"
        verbose_name_plural = "Tipos de Taxa"


class TaxaInscricao(models.Model):
    tipo_taxa = models.ForeignKey(TipoTaxa, on_delete=models.PROTECT)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, null=True, blank=True)
    instituicao = models.ForeignKey(Instituicao, on_delete=models.CASCADE, null=True, blank=True)
    pais = models.ForeignKey(Pais, on_delete=models.CASCADE, null=True, blank=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    moeda = models.CharField(max_length=3, default='Kz')
    ativo = models.BooleanField(default=True)
    
    def __str__(self):
        if self.curso:
            return f"{self.valor} {self.moeda} - {self.curso}"
        elif self.instituicao:
            return f"{self.valor} {self.moeda} - {self.instituicao}"
        else:
            return f"{self.valor} {self.moeda} - {self.pais}"
    
    def clean(self):
        # Garantir que apenas um relacionamento seja definido
        count = sum([bool(self.curso), bool(self.instituicao), bool(self.pais)])
        if count != 1:
            raise ValidationError("A taxa deve estar associada a um curso, instituição ou país, mas não a múltiplos.")
    
    class Meta:
        verbose_name = "Taxa de Inscrição"
        verbose_name_plural = "Taxas de Inscrição"


class Candidatura(models.Model):
    ESTADO_CHOICES = [
        ('rascunho', 'Rascunho'),
        ('submetida', 'Submetida'),
        ('em_analise', 'Em Análise'),
        ('aprovada', 'Aprovada'),
        ('rejeitada', 'Rejeitada'),
        ('matriculada', 'Matriculada'),
    ]
    
    codigo = models.CharField(max_length=20, unique=True, editable=False)
    nome_completo = models.CharField(max_length=255)
    email = models.EmailField()
    telefone = models.CharField(max_length=20)
    idade = models.PositiveIntegerField(null=True, blank=True)
    bi = models.CharField(max_length=14, null=True, blank=True)
    curso = models.ForeignKey(Curso, on_delete=models.PROTECT)
    instituicao = models.ForeignKey(Instituicao, on_delete=models.PROTECT)
    certificado = models.FileField(upload_to='certificados/')
    taxa_inscricao = models.ForeignKey(TaxaInscricao, on_delete=models.PROTECT)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='rascunho')
    data_submissao = models.DateTimeField(auto_now_add=True)
    data_actualizacao = models.DateTimeField(auto_now=True)
    termos_aceites = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.codigo} - {self.nome_completo}"
    

    def save(self, *args, **kwargs):
        if not self.codigo:
            # Gerar código único para a candidatura
            import uuid
            self.codigo = str(uuid.uuid4())[:8].upper()
        super().save(*args, **kwargs)  # CORRIGIDO: **kwargs em vez de kwargs
    
    class Meta:
        verbose_name = "Candidatura"
        verbose_name_plural = "Candidaturas"



class Depoimento(models.Model):
    nome = models.CharField(max_length=200)
    curso = models.ForeignKey(Curso, on_delete=models.SET_NULL, null=True)
    instituicao = models.ForeignKey(Instituicao, on_delete=models.SET_NULL, null=True)
    texto = models.TextField()
    foto = models.ImageField(upload_to='depoimentos/', blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nome} - {self.curso}"