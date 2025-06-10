document.addEventListener('DOMContentLoaded', () => {
    // Lista de ícones do Font Awesome (uma seleção para exemplo)
    const faIcons = [
        // Genéricos
        { name: "Foguete", class: "fas fa-rocket" }, { name: "Engrenagem", class: "fas fa-cog" },
        { name: "Estrela", class: "fas fa-star" }, { name: "Coração", class: "fas fa-heart" },
        { name: "Casa", class: "fas fa-home" }, { name: "Prédio", class: "fas fa-building" },
        { name: "Mundo", class: "fas fa-globe" }, { name: "Gráfico de Pizza", class: "fas fa-chart-pie" },
        { name: "Gráfico de Barras", class: "fas fa-chart-bar" }, { name: "Usuário", class: "fas fa-user" },
        { name: "Usuários", class: "fas fa-users" }, { name: "Cadeado", class: "fas fa-lock" },

        // Arquivos e Documentos
        { name: "Pasta", class: "fas fa-folder" }, { name: "Pasta Aberta", class: "fas fa-folder-open" },
        { name: "Arquivo", class: "fas fa-file-alt" }, { name: "Excel", class: "fas fa-file-excel" },
        { name: "Word", class: "fas fa-file-word" }, { name: "PowerPoint", class: "fas fa-file-powerpoint" },
        { name: "PDF", class: "fas fa-file-pdf" }, { name: "Imagem", class: "fas fa-file-image" },
        { name: "Código", class: "fas fa-file-code" },

        // Comunicação
        { name: "Envelope", class: "fas fa-envelope" }, { name: "Telefone", class: "fas fa-phone" },
        { name: "Comentário", class: "fas fa-comment" }, { name: "Sino", class: "fas fa-bell" },
        { name: "Skype", class: "fab fa-skype" }, { name: "WhatsApp", class: "fab fa-whatsapp" },

        // Outros
        { name: "Ticket", class: "fas fa-ticket-alt" }, { name: "Terminal", class: "fas fa-terminal" },
        { name: "Calculadora", class: "fas fa-calculator" }, { name: "Banco de Dados", class: "fas fa-database" },
        { name: "Windows", class: "fab fa-windows" }, { name: "Google", class: "fab fa-google" }
    ];

    const iconGrid = document.getElementById('icon-picker-grid');
    const searchInput = document.getElementById('icon-search');
    const modal = document.getElementById('icon-modal');
    const openModalBtn = document.getElementById('open-icon-picker');
    const closeModalBtn = document.querySelector('.icon-modal-close');
    const targetInput = document.getElementById('icon_class');

    // Função para renderizar os ícones na grade
    const renderIcons = (icons) => {
        if (!iconGrid) return;
        iconGrid.innerHTML = ''; // Limpa a grade
        icons.forEach(icon => {
            const iconElement = document.createElement('div');
            iconElement.className = 'icon-picker-item';
            iconElement.dataset.iconClass = icon.class; // Armazena a classe no elemento
            iconElement.innerHTML = `<i class="${icon.class}"></i><span>${icon.name}</span>`;
            
            // Adiciona evento de clique para selecionar o ícone
            iconElement.addEventListener('click', () => {
                if (targetInput) {
                    targetInput.value = icon.class; // Preenche o campo do formulário
                }
                if (modal) {
                    modal.style.display = 'none'; // Fecha o modal
                }
            });

            iconGrid.appendChild(iconElement);
        });
    };

    // Abre o modal
    if (openModalBtn) {
        openModalBtn.addEventListener('click', (e) => {
            e.preventDefault();
            if (modal) {
                modal.style.display = 'flex';
                renderIcons(faIcons); // Renderiza todos os ícones ao abrir
                searchInput.focus();
            }
        });
    }

    // Fecha o modal
    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', () => {
            if (modal) modal.style.display = 'none';
        });
    }
    if (modal) {
        window.addEventListener('click', (event) => {
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        });
    }

    // Filtra os ícones ao digitar na busca
    if (searchInput) {
        searchInput.addEventListener('keyup', () => {
            const searchTerm = searchInput.value.toLowerCase();
            const filteredIcons = faIcons.filter(icon =>
                icon.name.toLowerCase().includes(searchTerm) || icon.class.toLowerCase().includes(searchTerm)
            );
            renderIcons(filteredIcons);
        });
    }
});