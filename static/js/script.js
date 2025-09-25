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
    const internationalNote = document.getElementById('international-note');
    const universidadeSelect = document.getElementById('universidade');
    const cursoSelect = document.getElementById('curso');

    scholarshipOptions.classList.add('hidden');
    form.classList.remove('hidden');
    bolsaType.value = type;

    if (type === 'national') {
        formTitle.textContent = 'Candidatura — Bolsa Nacional';
        internationalNote.classList.add('hidden');
        // Mostrar apenas universidades de Angola
        Array.from(universidadeSelect.options).forEach(option => {
            if (option.value !== '') {
                option.style.display = option.dataset.pais === 'Angola' ? '' : 'none';
            } else {
                option.style.display = ''; // Manter a opção padrão visível
            }
        });
    } else {
        formTitle.textContent = 'Candidatura — Bolsa Internacional';
        internationalNote.classList.remove('hidden');
        // Mostrar apenas universidades internacionais (não Angola)
        Array.from(universidadeSelect.options).forEach(option => {
            if (option.value !== '') {
                option.style.display = option.dataset.pais !== 'Angola' ? '' : 'none';
            } else {
                option.style.display = ''; // Manter a opção padrão visível
            }
        });
    }

    // Reset seleções
    universidadeSelect.value = '';
    cursoSelect.innerHTML = '<option value="">Selecione o curso...</option>';
}

// O resto do JavaScript permanece igual...

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