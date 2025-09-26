import requests
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from .config1 import PRONTU_API_URL, PRONTU_TOKEN
from datetime import datetime, timedelta
from django.utils import timezone
from candidaturas.models import Candidatura, Instituicao, Curso
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

        try:
            candidatura = Candidatura.objects.get(codigo=temp_id, estado='pendente')
            curso = candidatura.curso
            if not curso.preco:
                logger.error(f"Curso {curso.id} não possui preço definido.")
                messages.error(request, "Erro: O curso selecionado não possui preço definido.")
                return redirect('home')
        except Candidatura.DoesNotExist:
            logger.error(f"Candidatura {temp_id} não encontrada em estado 'pendente'.")
            messages.error(request, "Erro ao localizar a candidatura. Contate o suporte.")
            return redirect('home')

        expiration = (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
        payload = {
            "currency": "AOA",
            "amount": float(curso.preco),
            "reference_id": temp_id,
            "source": 0,
            "cancel_url": f"http://localhost:8000/payments/callback/cancel/?reference_id={temp_id}",
            "return_url": f"http://localhost:8000/payments/callback/success/?reference_id={temp_id}",
            "expiration_date": expiration,
        }
        headers = {"Authorization": PRONTU_TOKEN}
        logger.debug(f"Enviando payload para Prontu: {payload}")
        try:
            response = requests.post(
                f"{PRONTU_API_URL}/v1/hosts/transactions-receive",
                json=payload,
                headers=headers
            )
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Erro na API Prontu: {str(e)}")
            messages.error(request, "Erro ao gerar link de pagamento. Tente novamente.")
            return redirect('home')

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
                'candidatura': {'codigo': temp_id},
            })
        else:
            logger.error(f"Erro na API Prontu: {response.text}")
            messages.error(request, "Erro ao gerar link de pagamento. Tente novamente.")
            return redirect('home')
    else:
        logger.warning("Requisição GET recebida em create_checkout, redirecionando para home.")
        return redirect('home')

@csrf_exempt
def callback_success(request):
    logger.debug(f"Requisição recebida em callback_success: {request.method} at {timezone.now()}")
    reference_id = request.GET.get('reference_id') if request.method == 'GET' else request.POST.get('reference_id') or request.POST.get('id')
    logger.debug(f"Callback Sucesso: reference_id={reference_id}")
    
    if request.method == 'POST':
        logger.warning("Webhook recebido, mas sem suporte local. Usando GET para confirmação.")
        return HttpResponse(status=200)
    
    else:
        # GET: Redirecionamento do navegador - Confirmar pagamento e atualizar candidatura
        if reference_id:
            try:
                candidatura = Candidatura.objects.get(codigo=reference_id, estado='pendente')
                curso = candidatura.curso
                # Simular verificação de pagamento (substituir por chamada API Prontu se possível)
                payload = {
                    "reference_id": reference_id,
                    "token": PRONTU_TOKEN
                }
                headers = {"Authorization": PRONTU_TOKEN}
                response = requests.get(f"{PRONTU_API_URL}/v1/hosts/transactions-status", params=payload, headers=headers)
                if response.status_code == 200 and response.json().get("data", {}).get("status", "").lower() in ["success", "paid"]:
                    # Mover certificado para o local final
                    temp_file_path = candidatura.certificado.path
                    final_file_name = f"{reference_id}_{os.path.basename(temp_file_path)}"
                    final_file_path = os.path.join(settings.MEDIA_ROOT, 'certificados', final_file_name)
                    os.makedirs(os.path.dirname(final_file_path), exist_ok=True)
                    with open(temp_file_path, 'rb') as temp_file, open(final_file_path, 'wb') as final_file:
                        final_file.write(temp_file.read())
                    os.remove(temp_file_path)
                    candidatura.certificado.name = final_file_path
                    candidatura.estado = 'submetida'
                    candidatura.save()
                    logger.debug(f"Candidatura {reference_id} atualizada para 'submetida' e certificado movido.")

                    # Enviar e-mail
                    try:
                        send_mail(
                            'Bem-vindo à Bolsa Emanuel Xirimbimbi!',
                            f'Olá {candidatura.nome_completo},\n\nSua candidatura {candidatura.codigo} foi confirmada com sucesso!\n\nVocê será notificado sobre os próximos passos em breve.\n\nObrigado!\nEquipe Bolsa Emanuel Xirimbimbi',
                            'no-reply@bolsaemanuel.com',
                            [candidatura.email],
                            fail_silently=False,
                        )
                        logger.debug(f"E-mail enviado para {candidatura.email}")
                    except Exception as e:
                        logger.error(f"Erro ao enviar e-mail para {candidatura.email}: {str(e)}")

                    messages.success(request, f"PAGAMENTO CONFIRMADO! Sua candidatura {candidatura.codigo} foi processada com sucesso. Um e-mail foi enviado para {candidatura.email}.")
                else:
                    logger.error(f"Status de pagamento inválido para {reference_id}: {response.text}")
                    messages.error(request, "Pagamento confirmado, mas a validação falhou. Contate o suporte.")
            except Candidatura.DoesNotExist:
                logger.error(f"Candidatura {reference_id} não encontrada para GET com estado 'pendente' at {timezone.now()}")
                messages.error(request, "Pagamento confirmado, mas a candidatura não foi identificada. Contate o suporte.")
        else:
            logger.error(f"Nenhum reference_id fornecido no GET at {timezone.now()}")
            messages.error(request, "Erro ao processar pagamento: ID da candidatura não fornecido.")
        
        return render(request, 'payments/success.html')

@csrf_exempt
def callback_cancel(request):
    logger.debug(f"Requisição recebida em callback_cancel: {request.method} at {timezone.now()}")
    reference_id = request.GET.get('reference_id') if request.method == 'GET' else request.POST.get('reference_id') or request.POST.get('id')
    logger.debug(f"Callback Cancel: reference_id={reference_id}")
    
    if request.method == 'POST':
        logger.warning("Webhook recebido, mas sem suporte local. Usando GET para cancelamento.")
        return HttpResponse(status=200)
    
    else:
        # GET: Redirecionamento do navegador
        if reference_id:
            try:
                candidatura = Candidatura.objects.get(codigo=reference_id, estado='pendente')
                os.remove(candidatura.certificado.path)
                candidatura.delete()
                logger.debug(f"Candidatura {reference_id} deletada devido a cancelamento.")
                messages.warning(request, f"PAGAMENTO CANCELADO. Sua candidatura {reference_id} não foi confirmada. Tente novamente ou contate o suporte.")
            except Candidatura.DoesNotExist:
                logger.warning(f"Candidatura {reference_id} não encontrada para cancelamento.")
                messages.warning(request, f"PAGAMENTO CANCELADO. Sua candidatura {reference_id} não foi confirmada. Tente novamente ou contate o suporte.")
        else:
            messages.error(request, "Erro ao processar cancelamento: ID da candidatura não fornecido.")
        
        return render(request, 'payments/cancel.html')

@csrf_exempt
def callback_general(request):
    logger.debug(f"Requisição recebida em callback_general: {request.method} at {timezone.now()}")
    if request.method == 'POST':
        logger.warning("Webhook recebido, mas sem suporte local. Usando GET para processamento.")
        return HttpResponse(status=200)
    
    else:
        logger.warning("Callback Geral (GET): Redirecionando para home.")
        messages.warning(request, "Acesso inválido ao callback geral.")
        return redirect('home')