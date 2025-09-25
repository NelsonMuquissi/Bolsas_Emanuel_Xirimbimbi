# candidaturas/management/commands/popular_dados_exemplo.py
from django.core.management.base import BaseCommand
from django.db import transaction
from candidaturas.models import Pais, TipoInstituicao, Instituicao, AreaEstudo, Curso

class Command(BaseCommand):
    help = 'Popula o banco de dados com dados de exemplo'

    def handle(self, *args, **options):
        self.stdout.write('🎯 Iniciando população de dados de exemplo...')
        
        with transaction.atomic():
            self.criar_paises()
            self.criar_tipos_instituicao()
            self.criar_areas_estudo()
            self.criar_instituicoes_nacionais()
            self.criar_instituicoes_internacionais()
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
            lisboa = Instituicao.objects.get(nome='Centro de Formação Profissional de Lisboa')
            
            cursos = [
                # Universidade Gregório Semedo (Universitário)
                {'nome': 'Direito', 'instituicao': ugs, 'area_estudo': direito, 'modalidade': 'presencial', 'duracao': 10, 'tipo': 'universitario', 'preco': 7500},
                {'nome': 'Economia', 'instituicao': ugs, 'area_estudo': economia, 'modalidade': 'presencial', 'duracao': 8, 'tipo': 'universitario', 'preco': 7000},
                {'nome': 'Engenharia Informática', 'instituicao': ugs, 'area_estudo': engenharia, 'modalidade': 'presencial', 'duracao': 10, 'tipo': 'universitario', 'preco': 8000},
                {'nome': 'Gestão de Empresas', 'instituicao': ugs, 'area_estudo': economia, 'modalidade': 'presencial', 'duracao': 8, 'tipo': 'universitario', 'preco': 7000},
                {'nome': 'Contabilidade e Auditoria', 'instituicao': ugs, 'area_estudo': economia, 'modalidade': 'presencial', 'duracao': 8, 'tipo': 'universitario', 'preco': 7000},
                
                # Universidade Belas (Universitário)
                {'nome': 'Arquitetura', 'instituicao': belas, 'area_estudo': arquitetura, 'modalidade': 'presencial', 'duracao': 10, 'tipo': 'universitario', 'preco': 8500},
                {'nome': 'Engenharia Civil', 'instituicao': belas, 'area_estudo': engenharia, 'modalidade': 'presencial', 'duracao': 10, 'tipo': 'universitario', 'preco': 8000},
                {'nome': 'Ciências da Comunicação', 'instituicao': belas, 'area_estudo': comunicacao, 'modalidade': 'presencial', 'duracao': 8, 'tipo': 'universitario', 'preco': 7500},
                {'nome': 'Relações Internacionais', 'instituicao': belas, 'area_estudo': psicologia, 'modalidade': 'presencial', 'duracao': 8, 'tipo': 'universitario', 'preco': 7500},
                {'nome': 'Psicologia', 'instituicao': belas, 'area_estudo': psicologia, 'modalidade': 'presencial', 'duracao': 10, 'tipo': 'universitario', 'preco': 8000},
                
                # Instituto Superior Politécnico Ndunduma (Técnico)
                {'nome': 'Engenharia Electrotécnica', 'instituicao': ndunduma, 'area_estudo': engenharia, 'modalidade': 'presencial', 'duracao': 6, 'tipo': 'tecnico', 'preco': 5000},
                {'nome': 'Engenharia Mecânica', 'instituicao': ndunduma, 'area_estudo': engenharia, 'modalidade': 'presencial', 'duracao': 6, 'tipo': 'tecnico', 'preco': 5000},
                {'nome': 'Gestão Industrial', 'instituicao': ndunduma, 'area_estudo': economia, 'modalidade': 'presencial', 'duracao': 4, 'tipo': 'tecnico', 'preco': 4500},
                {'nome': 'Informática de Gestão', 'instituicao': ndunduma, 'area_estudo': engenharia, 'modalidade': 'presencial', 'duracao': 4, 'tipo': 'tecnico', 'preco': 4500},
                {'nome': 'Enfermagem', 'instituicao': ndunduma, 'area_estudo': saude, 'modalidade': 'presencial', 'duracao': 6, 'tipo': 'tecnico', 'preco': 5500},
                
                # Centro de Formação Profissional de Lisboa (Técnico)
                {'nome': 'Técnico em Informática', 'instituicao': lisboa, 'area_estudo': educacao, 'modalidade': 'presencial', 'duracao': 3, 'tipo': 'tecnico', 'preco': 4000},
                {'nome': 'Formação em Gestão', 'instituicao': lisboa, 'area_estudo': economia, 'modalidade': 'presencial', 'duracao': 3, 'tipo': 'tecnico', 'preco': 4000},
            ]
            
            for data in cursos:
                curso, created = Curso.objects.get_or_create(
                    nome=data['nome'],
                    instituicao=data['instituicao'],
                    defaults={
                        'area_estudo': data['area_estudo'],
                        'modalidade': data['modalidade'],
                        'duracao': data['duracao'],
                        'tipo': data['tipo'],
                        'preco': data['preco'],
                    }
                )
                if created:
                    self.stdout.write(f'✅ Curso criado: {curso.nome} - {curso.instituicao.nome} (Tipo: {curso.tipo}, Preço: {curso.preco} Kz)')
                else:
                    self.stdout.write(f'ℹ️  Curso já existe: {curso.nome} - {curso.instituicao.nome}')

        except Exception as e:
            self.stdout.write(f'⚠️  Erro ao criar cursos: {e}')