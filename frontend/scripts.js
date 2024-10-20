document.getElementById('register-btn').addEventListener('click', async (event) => {
    event.preventDefault();  // Impede o refresh da página
    const name = document.getElementById('student-name').value;

    if (!name) {
        alert('Por favor, insira o nome do aluno.');
        return;
    }

    const registerButton = document.getElementById('register-btn');
    registerButton.disabled = true;  // Desabilita o botão enquanto aguarda
    document.getElementById('register-message').querySelector('p').innerText = "Aguardando leitura do cartão...";
    document.getElementById('register-message').classList.add('show');

    const response = await fetch('http://127.0.0.1:5000/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name })
    });

    const data = await response.json();
    registerButton.disabled = false;  // Habilita o botão novamente
    document.getElementById('register-message').querySelector('p').innerText = response.ok ? data.message : data.error;

    if (response.ok) {
        setTimeout(() => {
            document.getElementById('register-message').classList.remove('show');
        }, 2000);
    }
});

document.getElementById('access-btn').addEventListener('click', async () => {
    document.getElementById('access-message').querySelector('p').innerText = "Aguardando leitura do cartão...";
    document.getElementById('access-message').classList.add('show');

    try {
        const response = await fetch('http://127.0.0.1:5000/access', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();
        document.getElementById('access-message').querySelector('p').innerText = data.message || data.error;
    } catch (error) {
        document.getElementById('access-message').querySelector('p').innerText = `Erro: ${error.message}`;
    }

    setTimeout(() => {
        document.getElementById('access-message').classList.remove('show');
    }, 1500);
});

document.getElementById('list-btn').addEventListener('click', async () => {
    const userList = document.getElementById('user-list');
    userList.innerHTML = ''; // Limpa a lista antes de adicionar

    try {
        const response = await fetch('http://127.0.0.1:5000/list');
        const students = await response.json();

        for (const name in students) {
            const listItem = document.createElement('li');
            listItem.textContent = `${name}: ${students[name]}`;
            userList.appendChild(listItem);
        }

        document.getElementById('user-list-message').classList.add('show');
    } catch (error) {
        alert('Erro ao listar alunos.');
    }
});

// Lógica para fechar os popups
document.querySelectorAll('.close-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        this.parentElement.classList.remove('show');
    });
});
