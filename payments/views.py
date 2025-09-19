import requests
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from .config import PRONTU_API_URL, PRONTU_TOKEN
from datetime import datetime, timedelta
from django.utils import timezone
from candidaturas.models import Candidatura, Instituicao, Curso, TaxaInscricao
from django.core.mail import send_mail
import logging
import os
from django.core.files.base import ContentFile
from django.core.exceptions import ObjectDoesNotExist

logger = logging.getLogger(__name__)

def create_checkout(request):
    logger.debug(f"Requisição recebida em create_checkout: {request.method}")
    if request.method == 'POST':
        temp_id = request.session.get('temp_candidatura_id')
        logger.debug(f"Temp ID: {temp_id}")
        if not temp_id:
            logger.warning("Temp ID não encontrado na sessão.")
            messages.error(request, "Dados do formulário não encontrados. Preencha o formulário novamente.")
            return redirect('home')

        temp_data = request.session.get('temp_candidatura', {})
        temp_file_path = request.session.get('temp_certificado_path')

        if not temp_data or not temp_file_path:
            logger.warning("Dados temporários não encontrados na sessão.")
            messages.error(request, "Dados do formulário não encontrados. Preencha o formulário novamente.")
            return redirect('home')

        expiration = (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
        payload = {
            "currency": "AOA",
            "amount": float(temp_data['taxa_inscricao_id']),  # Valor da taxa
            "reference_id": temp_id,  # Usar temp_id como reference_id
            "source": 0,
            "cancel_url": f"http://localhost:8000/payments/callback/cancel/?reference_id={temp_id}",
            "return_url": f"http://localhost:8000/payments/callback/success/?reference_id={temp_id}",
            "expiration_date": expiration,
        }
        headers = {"Authorization": PRONTU_TOKEN}
        logger.debug(f"Enviando payload para Prontu: {payload}")
        response = requests.post(
            f"{PRONTU_API_URL}/v1/hosts/transactions-receive",
            json=payload,
            headers=headers
        )
        
        logger.debug(f"Resposta do Prontu: status={response.status_code}, body={response.text}")
        if response.status_code == 200:
            data = response.json()
            payment_url = data.get("data", {}).get("url", "")
            reference_id = data.get("data", {}).get("reference_id", payload.get("reference_id", "Prontu-Generated"))
            entity_id = data.get("data", {}).get("entity_id", "")
            return render(request, 'payments/checkout.html', {
                'payment_url': payment_url,
                'reference_id': reference_id,
                'amount': payload.get("amount"),
                'expiration_date': payload.get("expiration_date"),
                'entity_id': entity_id,
                'status': 'Iniciado',
                'candidatura': {'codigo': temp_id},  # Temp data for display
            })
        else:
            logger.error(f"Erro na API Prontu: {response.json()}")
            messages.error(request, "Erro ao gerar link de pagamento. Tente novamente.")
            return redirect('home')
    else:
        logger.warning("Requisição GET recebida em create_checkout, redirecionando para home.")
        return redirect('home')

@csrf_exempt
def callback_success(request):
    logger.debug(f"Requisição recebida em callback_success: {request.method}")
    reference_id = request.GET.get('reference_id') if request.method == 'GET' else request.POST.get('reference_id') or request.POST.get('id')
    logger.debug(f"Callback Sucesso: reference_id={reference_id}")
    if request.method == 'POST':
        # Webhook: Salvar candidatura e enviar e-mail
        temp_data = request.session.get('temp_candidatura', {})
        temp_file_path = request.session.get('temp_certificado_path')
        if not temp_data or not temp_file_path:
            logger.error("Dados temporários não encontrados na sessão durante webhook.")
            return HttpResponse(status=200)
        try:
            # Buscar entidades
            instituicao = Instituicao.objects.get(id=temp_data['universidade_id'])
            curso = Curso.objects.get(id=temp_data['curso_id'])
            taxa_inscricao = TaxaInscricao.objects.get(id=temp_data['taxa_inscricao_id'])

            # Salvar arquivo no local final
            with open(temp_file_path, 'rb') as temp_file:
                certificado_content = ContentFile(temp_file.read())
            final_file_name = f"{reference_id}_{os.path.basename(temp_file_path)}"
            final_file_path = os.path.join('certificados', final_file_name)

            # Salvar candidatura
            candidatura = Candidatura(
                codigo=reference_id,
                nome_completo=temp_data['nome_completo'],
                idade=int(temp_data['idade']) if temp_data['idade'] else None,
                bi=temp_data['bi'],
                telefone=temp_data['telefone'],
                email=temp_data['email'],
                curso=curso,
                instituicao=instituicao,
                taxa_inscricao=taxa_inscricao,
                certificado=final_file_path,  # Salvar como ContentFile
                termos_aceites=True,
                estado='submetida'
            )
            candidatura.save()

            # Enviar e-mail
            send_mail(
                'Bem-vindo à Bolsa Emanuel Xirimbimbi!',
                f'Olá {candidatura.nome_completo},\n\nSua candidatura {candidatura.codigo} foi confirmada com sucesso!\n\nVocê será notificado sobre os próximos passos em breve.\n\nObrigado!\nEquipe Bolsa Emanuel Xirimbimbi',
                'no-reply@bolsaemanuel.com',  # Substitua pelo e-mail real
                [candidatura.email],
                fail_silently=False,
            )

            # Limpar sessão
            if 'temp_candidatura' in request.session:
                del request.session['temp_candidatura']
            if 'temp_certificado_path' in request.session:
                del request.session['temp_certificado_path']
            if 'temp_candidatura_id' in request.session:
                del request.session['temp_candidatura_id']

            logger.debug(f"Candidatura {reference_id} salva e e-mail enviado.")
        except (ObjectDoesNotExist, Exception) as e:
            logger.error(f"Erro ao salvar candidatura no webhook: {str(e)}")
        return HttpResponse(status=200)
    else:
        # GET: Redirecionamento do navegador
        if reference_id:
            try:
                # Verificar se candidatura foi salva (webhook já executou)
                candidatura = Candidatura.objects.get(codigo=reference_id, estado='submetida')
                messages.success(request, f"Parabéns! Sua candidatura {candidatura.codigo} foi confirmada.")
                return render(request, 'payments/success.html', {'candidatura': candidatura})
            except Candidatura.DoesNotExist:
                logger.error(f"Candidatura {reference_id} não encontrada para GET (webhook pode ter falhado).")
                messages.error(request, "Erro ao confirmar pagamento. Tente novamente.")
        else:
            messages.error(request, "Erro ao processar pagamento.")
        return redirect('home')

@csrf_exempt
def callback_cancel(request):
    logger.debug(f"Requisição recebida em callback_cancel: {request.method}")
    reference_id = request.GET.get('reference_id') if request.method == 'GET' else request.POST.get('reference_id') or request.POST.get('id')
    logger.debug(f"Callback Cancel: reference_id={reference_id}")
    if request.method == 'POST':
        # Webhook: Limpar dados temporários
        if reference_id:
            temp_data = request.session.get('temp_candidatura', {})
            temp_file_path = request.session.get('temp_certificado_path')
            if temp_file_path and os.path.exists(temp_file_path):
                os.remove(temp_file_path)  # Deletar arquivo temporário
                logger.debug(f"Arquivo temporário deletado: {temp_file_path}")
            # Limpar sessão
            if 'temp_candidatura' in request.session:
                del request.session['temp_candidatura']
            if 'temp_certificado_path' in request.session:
                del request.session['temp_certificado_path']
            if 'temp_candidatura_id' in request.session:
                del request.session['temp_candidatura_id']
            logger.debug(f"Dados temporários limpos para {reference_id}.")
        return HttpResponse(status=200)
    else:
        # GET: Redirecionamento do navegador
        if reference_id:
            # Limpar dados temporários
            temp_data = request.session.get('temp_candidatura', {})
            temp_file_path = request.session.get('temp_certificado_path')
            if temp_file_path and os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            # Limpar sessão
            if 'temp_candidatura' in request.session:
                del request.session['temp_candidatura']
            if 'temp_certificado_path' in request.session:
                del request.session['temp_certificado_path']
            if 'temp_candidatura_id' in request.session:
                del request.session['temp_candidatura_id']
            messages.warning(request, f"Pagamento cancelado para candidatura {reference_id}. Preencha o formulário novamente se desejar tentar.")
        else:
            messages.error(request, "Erro ao processar cancelamento.")
        return render(request, 'payments/cancel.html')

@csrf_exempt
def callback_general(request):
    logger.debug(f"Requisição recebida em callback_general: {request.method}")
    if request.method == 'POST':
        data = request.POST
        logger.debug(f"Callback Geral: {data}")
        reference_id = data.get('reference_id') or data.get('id')
        if reference_id:
            # Mesma lógica do callback_success para salvar
            temp_data = request.session.get('temp_candidatura', {})
            temp_file_path = request.session.get('temp_certificado_path')
            if not temp_data or not temp_file_path:
                logger.error("Dados temporários não encontrados na sessão durante webhook.")
                return HttpResponse(status=200)
            try:
                instituicao = Instituicao.objects.get(id=temp_data['universidade_id'])
                curso = Curso.objects.get(id=temp_data['curso_id'])
                taxa_inscricao = TaxaInscricao.objects.get(id=temp_data['taxa_inscricao_id'])

                with open(temp_file_path, 'rb') as temp_file:
                    certificado_content = ContentFile(temp_file.read())
                final_file_name = f"{reference_id}_{os.path.basename(temp_file_path)}"
                final_file_path = os.path.join('certificados', final_file_name)

                candidatura = Candidatura(
                    codigo=reference_id,
                    nome_completo=temp_data['nome_completo'],
                    idade=int(temp_data['idade']) if temp_data['idade'] else None,
                    bi=temp_data['bi'],
                    telefone=temp_data['telefone'],
                    email=temp_data['email'],
                    curso=curso,
                    instituicao=instituicao,
                    taxa_inscricao=taxa_inscricao,
                    certificado=final_file_path,
                    termos_aceites=True,
                    estado='submetida'
                )
                candidatura.save()

                send_mail(
                    'Bem-vindo à Bolsa Emanuel Xirimbimbi!',
                    f'Olá {candidatura.nome_completo},\n\nSua candidatura {candidatura.codigo} foi confirmada com sucesso!\n\nVocê será notificado sobre os próximos passos em breve.\n\nObrigado!\nEquipe Bolsa Emanuel Xirimbimbi',
                    'no-reply@bolsaemanuel.com',
                    [candidatura.email],
                    fail_silently=False,
                )

                # Limpar sessão
                if 'temp_candidatura' in request.session:
                    del request.session['temp_candidatura']
                if 'temp_certificado_path' in request.session:
                    del request.session['temp_certificado_path']
                if 'temp_candidatura_id' in request.session:
                    del request.session['temp_candidatura_id']

                logger.debug(f"Candidatura {reference_id} salva e e-mail enviado.")
            except (ObjectDoesNotExist, Exception) as e:
                logger.error(f"Erro ao salvar candidatura no webhook: {str(e)}")
        return HttpResponse(status=200)
    else:
        logger.warning("Callback Geral (GET): Redirecionando para home.")
        messages.warning(request, "Acesso inválido ao callback geral.")
        return redirect('home')