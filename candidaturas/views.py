from django.shortcuts import render
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.db.models import Prefetch
from .models import Pais, Instituicao, Curso, Depoimento, Candidatura
import uuid
import logging
import os
from django.conf import settings

logger = logging.getLogger(__name__)

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
    
    # Separar cursos universitários e técnicos
    cursos_universitarios = Curso.objects.filter(tipo='universitario', ativo=True).select_related('instituicao__pais').order_by('instituicao__pais__nome', 'instituicao__nome', 'nome')
    cursos_tecnicos = Curso.objects.filter(tipo='tecnico', ativo=True).select_related('instituicao__pais').order_by('instituicao__pais__nome', 'instituicao__nome', 'nome')

    international_paises = Pais.objects.filter(nome__in=['Argentina', 'Uruguai', 'Espanha', 'Brasil', 'Portugal']).order_by('nome')
    
    international_data = {}
    for pais in international_paises:
        insts = list(Instituicao.objects.filter(
            pais=pais, 
            ativo=True
        ).prefetch_related(
            Prefetch('curso_set', queryset=Curso.objects.filter(ativo=True), to_attr='cursos_ativos')
        )[:3])  # Limitar a 3 instituições por país
        international_data[pais.nome] = insts
    
    testimonials = list(Depoimento.objects.filter(is_active=True)[:3])
    
    all_institutions = list(Instituicao.objects.filter(ativo=True).select_related('pais').order_by('pais__nome', 'nome')[:10])
    all_courses = list(Curso.objects.filter(ativo=True).select_related('instituicao__pais').order_by('instituicao__pais__nome', 'instituicao__nome', 'nome')[:20])
    international_paises_list = list(international_paises)
    
    context = {
        'national_institutions': national_institutions,
        'international_data': international_data,
        'cursos_universitarios': cursos_universitarios,
        'cursos_tecnicos': cursos_tecnicos,
        'testimonials': testimonials,
        'all_institutions': all_institutions,
        'all_courses': all_courses,
        'international_paises': international_paises_list,
        'national_fee': {'valor': '7500', 'moeda': 'Kz'},
        'standard_fee': {'valor': '10000', 'moeda': 'Kz'},
        'brasil_premium': {'valor': '20000', 'moeda': 'Kz'},
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

            temp_id = str(uuid.uuid4())[:8].upper()
            temp_file_path = os.path.join(settings.MEDIA_ROOT, 'temp_certificados', f'{temp_id}_{certificado.name}')
            os.makedirs(os.path.dirname(temp_file_path), exist_ok=True)
            with open(temp_file_path, 'wb+') as temp_file:
                for chunk in certificado.chunks():
                    temp_file.write(chunk)

            candidatura = Candidatura(
                codigo=temp_id,
                nome_completo=nome_completo,
                idade=int(idade) if idade else None,
                bi=bi,
                telefone=telefone,
                email=email,
                curso=curso,
                instituicao=instituicao,
                certificado=temp_file_path,
                termos_aceites=True,
                estado='pendente'
            )
            candidatura.save()

            request.session['temp_candidatura_id'] = temp_id

            return JsonResponse({
                'success': True,
                'message': 'Dados do formulário processados! Redirecionando para pagamento...',
                'temp_id': temp_id,
                'redirect_url': '/payments/create_checkout/'
            })

        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            logger.error(f"Erro ao processar o formulário: {str(e)}", exc_info=True)
            return JsonResponse({'error': f'Erro ao processar o formulário: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Método não permitido.'}, status=405)

def load_courses(request):
    instituicao_id = request.GET.get('instituicao_id')
    courses = Curso.objects.filter(instituicao_id=instituicao_id, ativo=True).values('id', 'nome', 'preco')
    return JsonResponse({'cursos': list(courses)})

def nacionais(request):
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
    
    context = {
        'national_institutions': national_institutions,
        'national_fee': {'valor': '7500', 'moeda': 'Kz'},
    }
    return render(request, 'nacionais.html', context)

def internacionais(request):
    international_paises = Pais.objects.filter(nome__in=['Argentina', 'Uruguai', 'Espanha', 'Brasil', 'Portugal']).order_by('nome')
    
    international_data = {}
    for pais in international_paises:
        insts = list(Instituicao.objects.filter(
            pais=pais, 
            ativo=True
        ).prefetch_related(
            Prefetch('curso_set', queryset=Curso.objects.filter(ativo=True), to_attr='cursos_ativos')
        ))
        international_data[pais.nome] = insts
    
    context = {
        'international_data': international_data,
        'standard_fee': {'valor': '10000', 'moeda': 'Kz'},
        'brasil_premium': {'valor': '20000', 'moeda': 'Kz'},
    }
    return render(request, 'internacionais.html', context)