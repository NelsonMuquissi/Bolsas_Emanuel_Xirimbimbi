from django.shortcuts import render
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.db.models import Prefetch
from .models import Pais, Instituicao, Curso, TaxaInscricao, Depoimento
from django.core.files.uploadedfile import UploadedFile
import uuid
import os
from django.conf import settings

def home(request):
    try:
        angola = Pais.objects.get(nome='Angola')
    except Pais.DoesNotExist:
        angola = None
    
    national_institutions = []
    if angola:
        national_institutions = list(Instituicao.objects.filter(
            pais=angola, 
            ativo=True
        ).prefetch_related(
            Prefetch('curso_set', queryset=Curso.objects.filter(ativo=True), to_attr='cursos_ativos')
        ))
    
    international_paises = Pais.objects.filter(nome__in=['Argentina', 'Uruguai', 'Espanha', 'Brasil', 'Portugal']).order_by('nome')
    
    international_data = {}
    for pais in international_paises:
        insts = list(Instituicao.objects.filter(
            pais=pais, 
            ativo=True
        ).prefetch_related(
            Prefetch('curso_set', queryset=Curso.objects.filter(ativo=True), to_attr='cursos_ativos')
        )[:3])
        international_data[pais.nome] = insts
    
    national_fee = None
    if angola:
        national_fee = TaxaInscricao.objects.filter(pais=angola, ativo=True).first()
    if not national_fee:
        national_fee = type('obj', (object,), {'valor': 7500, 'moeda': 'AOA', 'tipo_taxa__nome': 'Nacional'})()
    
    standard_fee = TaxaInscricao.objects.filter(ativo=True, pais__nome='Argentina').first()
    if not standard_fee:
        standard_fee = type('obj', (object,), {'valor': 10000, 'moeda': 'AOA', 'tipo_taxa__nome': 'Standard'})()
    
    brasil_premium = TaxaInscricao.objects.filter(ativo=True, pais__nome='Brasil', tipo_taxa__nome__icontains='premium').first()
    if not brasil_premium:
        brasil_premium = type('obj', (object,), {'valor': 20000, 'moeda': 'AOA', 'tipo_taxa__nome': 'Premium'})()
    
    testimonials = list(Depoimento.objects.filter(is_active=True)[:3])
    
    all_institutions = list(Instituicao.objects.filter(ativo=True).select_related('pais').order_by('pais__nome', 'nome'))
    all_courses = list(Curso.objects.filter(ativo=True).select_related('instituicao__pais').order_by('instituicao__pais__nome', 'instituicao__nome', 'nome'))
    international_paises_list = list(international_paises)
    
    context = {
        'national_institutions': national_institutions,
        'international_data': international_data,
        'national_fee': national_fee,
        'standard_fee': standard_fee,
        'brasil_premium': brasil_premium,
        'testimonials': testimonials,
        'all_institutions': all_institutions,
        'all_courses': all_courses,
        'international_paises': international_paises_list,
    }
    return render(request, 'home.html', context)

def apply(request):
    if request.method == 'POST':
        try:
            nome_completo = request.POST.get('nome')
            idade = request.POST.get('idade')
            bi = request.POST.get('bi')
            telefone = request.POST.get('tel')
            email = request.POST.get('email')
            bolsa_type = request.POST.get('bolsa-type')
            pais_nome = request.POST.get('pais')
            tipo_brasil = request.POST.get('tipo-brasil')
            universidade_id = request.POST.get('universidade')
            curso_id = request.POST.get('curso')
            termos = request.POST.get('termos')
            certificado = request.FILES.get('certificado')

            if not all([nome_completo, telefone, email, universidade_id, curso_id]):
                return JsonResponse({'error': 'Todos os campos obrigatórios devem ser preenchidos.'}, status=400)
            
            if not termos:
                return JsonResponse({'error': 'Você deve aceitar os termos e condições.'}, status=400)
            
            if not certificado or not certificado.name.endswith('.pdf'):
                return JsonResponse({'error': 'Por favor, envie um certificado em formato PDF.'}, status=400)

            try:
                instituicao = Instituicao.objects.get(id=universidade_id, ativo=True)
                curso = Curso.objects.get(id=curso_id, instituicao=instituicao, ativo=True)
            except (Instituicao.DoesNotExist, Curso.DoesNotExist):
                return JsonResponse({'error': 'Universidade ou curso inválido.'}, status=400)

            taxa_inscricao = None
            if bolsa_type == 'national':
                taxa_inscricao = TaxaInscricao.objects.filter(pais=instituicao.pais, ativo=True).first()
            else:
                if pais_nome == 'Brasil' and tipo_brasil == 'premium':
                    taxa_inscricao = TaxaInscricao.objects.filter(pais__nome='Brasil', tipo_taxa__nome__icontains='premium', ativo=True).first()
                else:
                    taxa_inscricao = TaxaInscricao.objects.filter(pais__nome=pais_nome, ativo=True).first() or TaxaInscricao.objects.filter(ativo=True).first()

            if not taxa_inscricao:
                return JsonResponse({'error': 'Taxa de inscrição não encontrada.'}, status=400)

            # Gerar ID temporário para referência
            temp_id = str(uuid.uuid4())[:8].upper()

            # Armazenar dados temporários na sessão (texto)
            request.session['temp_candidatura'] = {
                'temp_id': temp_id,
                'nome_completo': nome_completo,
                'idade': idade,
                'bi': bi,
                'telefone': telefone,
                'email': email,
                'bolsa_type': bolsa_type,
                'pais_nome': pais_nome,
                'tipo_brasil': tipo_brasil,
                'universidade_id': universidade_id,
                'curso_id': curso_id,
                'taxa_inscricao_id': taxa_inscricao.id,
                'termos': True,
            }

            # Salvar arquivo temporariamente
            temp_file_path = os.path.join(settings.MEDIA_ROOT, 'temp_certificados', f'{temp_id}_{certificado.name}')
            os.makedirs(os.path.dirname(temp_file_path), exist_ok=True)
            with open(temp_file_path, 'wb+') as temp_file:
                for chunk in certificado.chunks():
                    temp_file.write(chunk)
            request.session['temp_certificado_path'] = temp_file_path

            request.session['temp_candidatura_id'] = temp_id  # Para referência no Prontu

            return JsonResponse({
                'success': True,
                'message': 'Dados do formulário processados! Redirecionando para pagamento...',
                'temp_id': temp_id,
                'redirect_url': '/payments/create_checkout/'
            })

        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Erro ao processar o formulário: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Método não permitido.'}, status=405)