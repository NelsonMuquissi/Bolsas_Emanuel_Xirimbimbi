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
            option.style.display = (option.dataset.pais === 'Angola' || option.value === '') ? '' : 'none';
        });
    } else {
        formTitle.textContent = 'Candidatura — Bolsa Internacional';
        paisContainer.classList.add('hidden'); // Removido o seletor de país para internacionais
        internationalNote.classList.remove('hidden');
        tipoBrasilContainer.classList.remove('hidden');
        Array.from(universidadeSelect.options).forEach(option => {
            option.style.display = (option.dataset.pais !== 'Angola' || option.value === '') ? '' : 'none';
        });
    }

    // Reset curso select
    cursoSelect.innerHTML = '<option value="">Selecione o curso...</option>';
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

document.getElementById('universidade').addEventListener('change', function() {
    const instituicaoId = this.value;
    const cursoSelect = document.getElementById('curso');
    const submitBtn = document.getElementById('submit-btn');
    const submitSpinner = document.getElementById('submit-spinner');

    if (instituicaoId) {
        submitBtn.disabled = true;
        submitSpinner.classList.remove('hidden');
        fetch(`/load-courses/?instituicao_id=${instituicaoId}`, {
            method: 'GET',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            cursoSelect.innerHTML = '<option value="">Selecione o curso...</option>';
            data.cursos.forEach(curso => {
                const option = document.createElement('option');
                option.value = curso.id;
                option.textContent = `${curso.nome} (Preço: ${curso.preco} Kz)`;
                cursoSelect.appendChild(option);
            });
            submitBtn.disabled = false;
            submitSpinner.classList.add('hidden');
        })
        .catch(error => {
            console.error('Erro ao carregar cursos:', error);
            submitBtn.disabled = false;
            submitSpinner.classList.add('hidden');
        });
    } else {
        cursoSelect.innerHTML = '<option value="">Selecione o curso...</option>';
    }
});

document.getElementById('applicationForm').addEventListener('submit', function(event) {
    event.preventDefault();
    const submitBtn = document.getElementById('submit-btn');
    const submitSpinner = document.getElementById('submit-spinner');

    if (this.checkValidity()) {
        submitBtn.disabled = true;
        submitSpinner.classList.remove('hidden');
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
            if (data.success) {
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
                alert(`Erro: ${data.error}`);
                submitBtn.disabled = false;
                submitSpinner.classList.add('hidden');
            }
        })
        .catch(error => {
            console.error('Erro no fetch:', error);
            alert('Erro ao processar o formulário. Tente novamente.');
            submitBtn.disabled = false;
            submitSpinner.classList.add('hidden');
        });
    } else {
        this.classList.add('was-validated');
    }
});