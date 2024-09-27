document.addEventListener('DOMContentLoaded', function() {
    obterTarefas();
});

function obterTarefas() {
    fetch('/tarefas')
        .then(response => response.json())
        .then(data => {
            const listaTarefas = document.getElementById('tarefas');
            listaTarefas.innerHTML = '';
            data.forEach(tarefa => {
                const li = document.createElement('li');
                li.className = 'tarefa';
                li.innerHTML = `
                    <strong>${tarefa.titulo}</strong>: ${tarefa.descricao}
                    <div class="botao-container">
                        <button onclick="deletarTarefa(${tarefa.id})">Excluir</button>
                        <button onclick="editarTarefa(${tarefa.id}, '${tarefa.titulo}', '${tarefa.descricao}')">Editar</button>
                    </div>
                `;
                listaTarefas.appendChild(li);
            });
        });
}

function adicionarTarefa() {
    const titulo = document.getElementById('titulo').value;
    const descricao = document.getElementById('descricao').value;

    fetch('/tarefas', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ titulo, descricao}),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Erro na requisição');
        }
        return response.json();
     })
     .then(data => {
        obterTarefas();
     })
     .catch(error => {
        console.error('Erro ao adicionar tarefa:', error);
     });
}

function editarTarefa(id, tituloAntigo, descricaoAntiga) {
    const novoTitulo = prompt("Edite o título da tarefa:", tituloAntigo);
    const novaDescricao = prompt("Edite a descrição da tarefa:", descricaoAntiga);

    if (novoTitulo && novaDescricao) {
        fetch(`/tarefas/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ titulo: novoTitulo, descricao: novaDescricao }),
        })
        .then(response => response.json())
        .then(() => {
            obterTarefas();
        });
    }
}

function deletarTarefa(id) {
    fetch(`/tarefas/${id}`, {
        method: 'DELETE',
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Erro ao excluir a tarefa');
        }
        obterTarefas(); // Atualiza a lista de tarefas após a exclusão
    })
    .catch(error => {
        console.error('Erro ao excluir tarefa:', error);
    });
}
