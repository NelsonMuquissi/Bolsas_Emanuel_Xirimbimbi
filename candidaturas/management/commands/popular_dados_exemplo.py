# candidaturas/management/commands/popular_dados_exemplo.py
from django.core.management.base import BaseCommand
from django.db import transaction
from candidaturas.models import Pais, TipoInstituicao, Instituicao, AreaEstudo, Curso, TipoTaxa, TaxaInscricao

class Command(BaseCommand):
    help = 'Popula o banco de dados com dados de exemplo'

    def handle(self, *args, **options):
        self.stdout.write('🎯 Iniciando população de dados de exemplo...')
        
        with transaction.atomic():
            self.criar_paises()
            self.criar_tipos_instituicao()
            self.criar_areas_estudo()
            self.criar_tipos_taxa()
            self.criar_instituicoes_nacionais()
            self.criar_instituicoes_internacionais()
            self.criar_taxas_inscricao()
            self.criar_cursos()
        
        self.stdout.write(
            self.style.SUCCESS('✅ Dados de exemplo populados com sucesso!')
        )

    def criar_paises(self):
        paises = [
            {'nome': 'Angola', 'codigo': 'AO'},
            {'nome': 'Argentina', 'codigo': 'AR'},
            {'nome': 'Brasil', 'codigo': 'BR'},
            {'nome': 'Portugal', 'codigo': 'PT'},
            {'nome': 'Uruguai', 'codigo': 'UY'},
            {'nome': 'Espanha', 'codigo': 'ES'},
        ]
        
        for data in paises:
            pais, created = Pais.objects.get_or_create(
                nome=data['nome'],
                defaults={'codigo': data['codigo']}
            )
            if created:
                self.stdout.write(f'✅ País criado: {pais.nome}')
            else:
                self.stdout.write(f'ℹ️  País já existe: {pais.nome}')

    def criar_tipos_instituicao(self):
        tipos = [
            {'nome': 'Universidade'},
            {'nome': 'Instituto Politécnico'},
            {'nome': 'Centro de Formação'},
            {'nome': 'Escola Superior'},
        ]
        
        for data in tipos:
            tipo, created = TipoInstituicao.objects.get_or_create(**data)
            if created:
                self.stdout.write(f'✅ Tipo de Instituição criado: {tipo.nome}')
            else:
                self.stdout.write(f'ℹ️  Tipo de Instituição já existe: {tipo.nome}')

    def criar_areas_estudo(self):
        areas = [
            {'nome': 'Direito e Ciências Jurídicas'},
            {'nome': 'Economia e Gestão'},
            {'nome': 'Engenharia e Tecnologia'},
            {'nome': 'Ciências da Saúde'},
            {'nome': 'Arquitetura e Urbanismo'},
            {'nome': 'Comunicação Social'},
            {'nome': 'Psicologia e Ciências Sociais'},
            {'nome': 'Educação e Formação'},
            {'nome': 'Artes e Design'},
            {'nome': 'Ciências Agrárias e Veterinária'},
        ]
        
        for data in areas:
            area, created = AreaEstudo.objects.get_or_create(**data)
            if created:
                self.stdout.write(f'✅ Área de Estudo criada: {area.nome}')
            else:
                self.stdout.write(f'ℹ️  Área de Estudo já existe: {area.nome}')

    def criar_tipos_taxa(self):
        tipos_taxa = [
            {'nome': 'Bolsa Nacional', 'descricao': 'Taxa para candidaturas nacionais'},
            {'nome': 'Bolsa Internacional', 'descricao': 'Taxa para candidaturas internacionais'},
            {'nome': 'Curso Premium', 'descricao': 'Taxa para cursos premium'},
            {'nome': 'Curso Técnico', 'descricao': 'Taxa para cursos técnicos/profissionais'},
        ]
        
        for data in tipos_taxa:
            tipo, created = TipoTaxa.objects.get_or_create(**data)
            if created:
                self.stdout.write(f'✅ Tipo de Taxa criado: {tipo.nome}')
            else:
                self.stdout.write(f'ℹ️  Tipo de Taxa já existe: {tipo.nome}')

    def criar_instituicoes_nacionais(self):
        try:
            angola = Pais.objects.get(nome='Angola')
            universidade = TipoInstituicao.objects.get(nome='Universidade')
            instituto = TipoInstituicao.objects.get(nome='Instituto Politécnico')
            
            instituicoes = [
                {'nome': 'Universidade Gregório Semedo', 'pais': angola, 'tipo': universidade},
                {'nome': 'Universidade Belas', 'pais': angola, 'tipo': universidade},
                {'nome': 'Instituto Superior Politécnico Ndunduma', 'pais': angola, 'tipo': instituto},
            ]
            
            for data in instituicoes:
                inst, created = Instituicao.objects.get_or_create(
                    nome=data['nome'],
                    pais=data['pais'],
                    defaults={'tipo': data['tipo']}
                )
                if created:
                    self.stdout.write(f'✅ Instituição Nacional criada: {inst.nome}')
                else:
                    self.stdout.write(f'ℹ️  Instituição Nacional já existe: {inst.nome}')
                    
        except Exception as e:
            self.stdout.write(f'⚠️  Erro ao criar instituições nacionais: {e}')

    def criar_instituicoes_internacionais(self):
        try:
            argentina = Pais.objects.get(nome='Argentina')
            brasil = Pais.objects.get(nome='Brasil')
            portugal = Pais.objects.get(nome='Portugal')
            uruguai = Pais.objects.get(nome='Uruguai')
            espanha = Pais.objects.get(nome='Espanha')
            
            universidade = TipoInstituicao.objects.get(nome='Universidade')
            centro_formacao = TipoInstituicao.objects.get(nome='Centro de Formação')
            
            instituicoes = [
                # Argentina
                {'nome': 'Universidade de Buenos Aires (UBA)', 'pais': argentina, 'tipo': universidade},
                {'nome': 'Universidade de Ciências Económicas e Sociais (UCES)', 'pais': argentina, 'tipo': universidade},
                {'nome': 'Universidade de Kennedy (UK)', 'pais': argentina, 'tipo': universidade},
                {'nome': 'Universidade do Museu Social Argentino (UMSA)', 'pais': argentina, 'tipo': universidade},
                
                # Uruguai
                {'nome': 'Universidade da Empresa (UDE)', 'pais': uruguai, 'tipo': universidade},
                
                # Espanha
                {'nome': 'Universidade de Girona', 'pais': espanha, 'tipo': universidade},
                
                # Brasil - Padrão
                {'nome': 'Universidade Cidade de São Paulo (Unicid)', 'pais': brasil, 'tipo': universidade},
                {'nome': 'Universidade Cruzeiro do Sul', 'pais': brasil, 'tipo': universidade},
                {'nome': 'Universidade FMU', 'pais': brasil, 'tipo': universidade},
                {'nome': 'Universidade São Judas (EAD)', 'pais': brasil, 'tipo': universidade},
                {'nome': 'Universidade Anhembi Morumbi', 'pais': brasil, 'tipo': universidade},
                {'nome': 'Universidade Braz Cubas', 'pais': brasil, 'tipo': universidade},
                
                # Brasil - Premium
                {'nome': 'Universidade Cidade de São Paulo (Unicid) - Premium', 'pais': brasil, 'tipo': universidade, 'premium': True},
                {'nome': 'Universidade Cruzeiro do Sul - Premium', 'pais': brasil, 'tipo': universidade, 'premium': True},
                {'nome': 'Universidade FMU - Premium', 'pais': brasil, 'tipo': universidade, 'premium': True},
                
                # Portugal
                {'nome': 'Centro de Formação Profissional de Lisboa', 'pais': portugal, 'tipo': centro_formacao},
            ]
            
            for data in instituicoes:
                premium = data.pop('premium', False) if 'premium' in data else False
                
                inst, created = Instituicao.objects.get_or_create(
                    nome=data['nome'],
                    pais=data['pais'],
                    defaults={
                        'tipo': data['tipo'],
                        'premium': premium
                    }
                )
                
                if created:
                    self.stdout.write(f'✅ Instituição Internacional criada: {inst.nome}')
                else:
                    # Atualiza se já existir
                    if inst.premium != premium:
                        inst.premium = premium
                        inst.save()
                        self.stdout.write(f'↗️  Instituição atualizada: {inst.nome} (Premium: {premium})')
                    else:
                        self.stdout.write(f'ℹ️  Instituição Internacional já existe: {inst.nome}')
                        
        except Exception as e:
            self.stdout.write(f'⚠️  Erro ao criar instituições internacionais: {e}')

    def criar_taxas_inscricao(self):
        try:
            tipo_nacional = TipoTaxa.objects.get(nome='Bolsa Nacional')
            tipo_internacional = TipoTaxa.objects.get(nome='Bolsa Internacional')
            tipo_premium = TipoTaxa.objects.get(nome='Curso Premium')
            tipo_tecnico = TipoTaxa.objects.get(nome='Curso Técnico')
            
            angola = Pais.objects.get(nome='Angola')
            portugal = Pais.objects.get(nome='Portugal')
            
            taxas = [
                # Taxas por país
                {'tipo_taxa': tipo_nacional, 'pais': angola, 'valor': 7500, 'moeda': 'Kz'},
                {'tipo_taxa': tipo_internacional, 'valor': 10000, 'moeda': 'Kz'},
                {'tipo_taxa': tipo_premium, 'valor': 20000, 'moeda': 'Kz'},
                {'tipo_taxa': tipo_tecnico, 'pais': portugal, 'valor': 5000, 'moeda': 'Kz'},
            ]
            
            for data in taxas:
                # Para taxas com país, use pais como filtro
                if 'pais' in data:
                    taxa, created = TaxaInscricao.objects.get_or_create(
                        tipo_taxa=data['tipo_taxa'],
                        pais=data['pais'],
                        defaults={'valor': data['valor'], 'moeda': data['moeda']}
                    )
                else:
                    # Para taxas sem país específico
                    taxa, created = TaxaInscricao.objects.get_or_create(
                        tipo_taxa=data['tipo_taxa'],
                        pais__isnull=True,
                        defaults={'valor': data['valor'], 'moeda': data['moeda']}
                    )
                
                if created:
                    self.stdout.write(f'✅ Taxa criada: {taxa}')
                else:
                    self.stdout.write(f'ℹ️  Taxa já existe: {taxa}')
                    
        except Exception as e:
            self.stdout.write(f'⚠️  Erro ao criar taxas: {e}')

    def criar_cursos(self):
        try:
            # Áreas de estudo
            direito = AreaEstudo.objects.get(nome='Direito e Ciências Jurídicas')
            economia = AreaEstudo.objects.get(nome='Economia e Gestão')
            engenharia = AreaEstudo.objects.get(nome='Engenharia e Tecnologia')
            saude = AreaEstudo.objects.get(nome='Ciências da Saúde')
            arquitetura = AreaEstudo.objects.get(nome='Arquitetura e Urbanismo')
            comunicacao = AreaEstudo.objects.get(nome='Comunicação Social')
            psicologia = AreaEstudo.objects.get(nome='Psicologia e Ciências Sociais')
            educacao = AreaEstudo.objects.get(nome='Educação e Formação')
            
            # Instituições nacionais
            ugs = Instituicao.objects.get(nome='Universidade Gregório Semedo')
            belas = Instituicao.objects.get(nome='Universidade Belas')
            ndunduma = Instituicao.objects.get(nome='Instituto Superior Politécnico Ndunduma')
            
            cursos_nacionais = [
                # UGS
                {'nome': 'Direito', 'instituicao': ugs, 'area_estudo': direito, 'modalidade': 'presencial', 'duracao': 10},
                {'nome': 'Economia', 'instituicao': ugs, 'area_estudo': economia, 'modalidade': 'presencial', 'duracao': 8},
                {'nome': 'Engenharia Informática', 'instituicao': ugs, 'area_estudo': engenharia, 'modalidade': 'presencial', 'duracao': 10},
                {'nome': 'Gestão de Empresas', 'instituicao': ugs, 'area_estudo': economia, 'modalidade': 'presencial', 'duracao': 8},
                {'nome': 'Contabilidade e Auditoria', 'instituicao': ugs, 'area_estudo': economia, 'modalidade': 'presencial', 'duracao': 8},
                
                # Belas
                {'nome': 'Arquitetura', 'instituicao': belas, 'area_estudo': arquitetura, 'modalidade': 'presencial', 'duracao': 10},
                {'nome': 'Engenharia Civil', 'instituicao': belas, 'area_estudo': engenharia, 'modalidade': 'presencial', 'duracao': 10},
                {'nome': 'Ciências da Comunicação', 'instituicao': belas, 'area_estudo': comunicacao, 'modalidade': 'presencial', 'duracao': 8},
                {'nome': 'Relações Internacionais', 'instituicao': belas, 'area_estudo': psicologia, 'modalidade': 'presencial', 'duracao': 8},
                {'nome': 'Psicologia', 'instituicao': belas, 'area_estudo': psicologia, 'modalidade': 'presencial', 'duracao': 10},
                
                # Ndunduma
                {'nome': 'Engenharia Electrotécnica', 'instituicao': ndunduma, 'area_estudo': engenharia, 'modalidade': 'presencial', 'duracao': 10},
                {'nome': 'Engenharia Mecânica', 'instituicao': ndunduma, 'area_estudo': engenharia, 'modalidade': 'presencial', 'duracao': 10},
                {'nome': 'Gestão Industrial', 'instituicao': ndunduma, 'area_estudo': economia, 'modalidade': 'presencial', 'duracao': 8},
                {'nome': 'Informática de Gestão', 'instituicao': ndunduma, 'area_estudo': engenharia, 'modalidade': 'presencial', 'duracao': 8},
                {'nome': 'Enfermagem', 'instituicao': ndunduma, 'area_estudo': saude, 'modalidade': 'presencial', 'duracao': 8},
            ]
            
            for data in cursos_nacionais:
                curso, created = Curso.objects.get_or_create(
                    nome=data['nome'],
                    instituicao=data['instituicao'],
                    defaults={
                        'area_estudo': data['area_estudo'],
                        'modalidade': data['modalidade'],
                        'duracao': data['duracao']
                    }
                )
                if created:
                    self.stdout.write(f'✅ Curso Nacional criado: {curso.nome} - {curso.instituicao.nome}')
                else:
                    self.stdout.write(f'ℹ️  Curso Nacional já existe: {curso.nome} - {curso.instituicao.nome}')
                    
        except Exception as e:
            self.stdout.write(f'⚠️  Erro ao criar cursos: {e}')