Bolsa Emanuel Xirimbimbi
Sistema de gerenciamento de candidaturas para bolsas de estudo nacionais e internacionais.
Pré-requisitos

Python 3.13.5
Django 5.2.6
Git

Instalação

Clone o repositório:
git clone <URL_DO_REPOSITORIO>
cd Final


Crie e ative um ambiente virtual:
python -m venv venv
source venv/Scripts/activate  # Windows
# ou: source venv/bin/activate  # Linux/Mac


Instale as dependências:
pip install -r requirements.txt


Configure as variáveis de ambiente:

Crie payments/config.py com:PRONTU_API_URL = 'https://api.prontu.io'
PRONTU_TOKEN = 'SEU_TOKEN_AQUI'


Configure o e-mail em bolsas_emanuel/settings.py (e.g., Gmail SMTP):EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'seu-email@gmail.com'
EMAIL_HOST_PASSWORD = 'sua-senha-app'
DEFAULT_FROM_EMAIL = 'no-reply@bolsaemanuel.com'




Aplique as migrações:
python manage.py makemigrations
python manage.py migrate


Crie um superusuário (opcional):
python manage.py createsuperuser


Inicie o servidor:
python manage.py runserver


Acesse em http://127.0.0.1:8000.


Estrutura do Projeto

bolsas_emanuel/: Configurações do Django.
candidaturas/: Modelos, views e URLs para gerenciamento de candidaturas.
payments/: Integração com Prontu API para pagamentos.
static/: Arquivos CSS e JavaScript.
templates/: Templates Django (home.html).
media/: Arquivos de upload (certificados).

Fluxo de Candidatura

Preencha o formulário em /.
Dados são armazenados temporariamente na sessão.
Redirecionado para checkout (/payments/create_checkout/).
Após pagamento:
Sucesso: Candidatura salva, e-mail enviado, redireciona para /payments/callback/success/.
Cancelamento: Dados descartados, redireciona para /payments/callback/cancel/.



Notas

Não versionar payments/config.py (contém credenciais).
Configure um servidor SMTP para e-mails.
Use um servidor WSGI/ASGI em produção (veja Django Deployment Docs).

Contato
Para dúvidas, contate emelsonmuquissi@gmail.com