function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function showForm(type) {
    const form = document.getElementById('application-form');
    const scholarshipOptions = document.getElementById('scholarship-options');
    const formTitle = document.getElementById('form-title');
    const bolsaType = document.getElementById('bolsa-type');
    const paisContainer = document.getElementById('pais-container');
    const tipoBrasilContainer = document.getElementById('tipo-brasil-container');
    const internationalNote = document.getElementById('international-note');
    const universidadeSelect = document.getElementById('universidade');
    const cursoSelect = document.getElementById('curso');

    scholarshipOptions.classList.add('hidden');
    form.classList.remove('hidden');
    bolsaType.value = type;

    if (type === 'national') {
        formTitle.textContent = 'Candidatura — Bolsa Nacional';
        paisContainer.classList.add('hidden');
        tipoBrasilContainer.classList.add('hidden');
        internationalNote.classList.add('hidden');
        Array.from(universidadeSelect.options).forEach(option => {
            option.style.display = option.dataset.pais === 'Angola' || option.value === '' ? '' : 'none';
        });
    } else {
        formTitle.textContent = 'Candidatura — Bolsa Internacional';
        paisContainer.classList.remove('hidden');
        internationalNote.classList.remove('hidden');
        Array.from(universidadeSelect.options).forEach(option => {
            option.style.display = '';
        });
    }

    universidadeSelect.addEventListener('change', function() {
        const selectedUniId = this.value;
        Array.from(cursoSelect.options).forEach(option => {
            option.style.display = option.dataset.uni === selectedUniId || option.value === '' ? '' : 'none';
        });
    }, { once: true });

    document.getElementById('pais').addEventListener('change', function() {
        tipoBrasilContainer.classList.toggle('hidden', this.value !== 'Brasil');
    }, { once: true });
}

function hideForm() {
    const form = document.getElementById('application-form');
    const scholarshipOptions = document.getElementById('scholarship-options');
    form.classList.add('hidden');
    scholarshipOptions.classList.remove('hidden');
    document.getElementById('applicationForm').reset();
}

function scrollToInscricao() {
    document.getElementById('inscricao').scrollIntoView({ behavior: 'smooth' });
}

document.getElementById('applicationForm').addEventListener('submit', function(event) {
    event.preventDefault();
    if (this.checkValidity()) {
        const formData = new FormData(this);
        
        fetch('/apply/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            console.log('Dados recebidos:', data);
            if (data.success) {
                // Redirecionamento direto sem alert
                const form = document.createElement('form');
                form.method = 'POST';
                form.action = '/payments/create_checkout/';
                const input = document.createElement('input');
                input.type = 'hidden';
                input.name = 'candidatura_codigo';
                input.value = data.temp_id;
                form.appendChild(input);
                const csrfInput = document.createElement('input');
                csrfInput.type = 'hidden';
                csrfInput.name = 'csrfmiddlewaretoken';
                csrfInput.value = getCookie('csrftoken');
                form.appendChild(csrfInput);
                document.body.appendChild(form);
                form.submit();
            } else {
                console.error('Erro na submissão:', data.error);
                alert(`Erro: ${data.error}`);
            }
        })
        .catch(error => {
            console.error('Erro no fetch:', error);
            alert('Erro ao processar o formulário. Tente novamente.');
        });
    } else {
        this.classList.add('was-validated');
    }
});