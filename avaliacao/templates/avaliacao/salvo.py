{% load static %}

<html lang="pt">
<head>
    <meta charset="UTF-8">
    <title>Perfil de {{ colaborador.nome }}</title>
    <link rel="icon" type="image/x-icon" href="{% static 'assets/favicon.ico'%}" />
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.7.0/chart.min.js"></script>
    <style>
        :root {
            --primary-color: #3498DB;
            --secondary-color: #475569;
            --background-color: #f8fafc;
            --card-background: #ffffff;
        }

        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            margin: 0;
            padding: 0;
            background-color: var(--background-color);
            color: var(--secondary-color);
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }

        .header {
            background-color: var(--primary-color);
            color: white;
            padding: 2rem;
            margin-bottom: 2rem;
            border-radius: 0 0 1rem 1rem;
            box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        }

        .header h1 {
            margin: 0;
            font-size: 2.5rem;
        }

        .profile-info {
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 2rem;
            margin-bottom: 2rem;
        }

        .profile-card {
            background-color: var(--card-background);
            border-radius: 1rem;
            padding: 2rem;
            box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        }

        .avatar {
            width: 150px;
            height: 150px;
            border-radius: 50%;
            background-color: #e2e8f0;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 1rem;
            font-size: 3rem;
            color: var(--primary-color);
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }

        .stat-card {
            background-color: var(--card-background);
            border-radius: 0.75rem;
            padding: 1.5rem;
            box-shadow: 0 2px 4px -1px rgb(0 0 0 / 0.1);
        }

        .stat-card h3 {
            margin: 0 0 0.5rem 0;
            color: var(--primary-color);
        }

        .chart-container {
            background-color: var(--card-background);
            border-radius: 1rem;
            padding: 2rem;
            box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        }

        .score {
            font-size: 2rem;
            font-weight: bold;
            color: var(--primary-color);
        }

        .trend {
            font-size: 0.875rem;
            color: #10b981;
        }

        .excellent {
            color: green;
        }
        
        .good {
            color: blue;
        }
        
        .average {
            color: orange;
        }
        
        .poor {
            color: red;
        }
        /* Estilos para o botão */
        #toggleCommentsButton {
            background: linear-gradient(135deg, #6e8efb, #a777e3); /* Gradiente de cor */
            border: none;
            color: white;
            padding: 10px 20px;
            font-size: 16px;
            font-weight: bold;
            border-radius: 25px; /* Botão arredondado */
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); /* Sombra sutil */
        }
    
        /* Efeito de hover no botão */
        #toggleCommentsButton:hover {
            background: linear-gradient(135deg, #a777e3, #6e8efb); /* Inverte o gradiente no hover */
            transform: scale(1.05); /* Aumenta levemente o botão */
            box-shadow: 0 6px 10px rgba(0, 0, 0, 0.15); /* Sombra mais intensa no hover */
        }
    
        /* Efeito de foco no botão */
        #toggleCommentsButton:focus {
            outline: none;
            box-shadow: 0 0 5px rgba(0, 123, 255, 0.5); /* Efeito de foco */
        }

        
        
    </style>
</head>
<body>
    <div class="header">
        {% comment %} <div class="container"> {% endcomment %}
            <h4>
                <a href="{% url 'home' %}" style="color: white;" class="name-link">Voltar pro inicio</a>
            </h4>
        </div> 
    </div>
    
    <!-- Adicionando o Font Awesome no cabeçalho -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css" />
    
    <!-- Botão fixado no lado direito -->
    <a href="{% url 'feedback_colaborador' colaborador_id=colaborador.id %}">
        <button class="social-btn">
            <i class="fas fa-robot"></i> Guia de feedback com IA
        </button>
    </a>
    

    <div class="container">
        <div class="profile-info">
            <div class="profile-card">
                <div class="avatar">
                    {{ colaborador.nome.0 }}
                </div>
                
                <h2 style="text-align: center; margin-bottom: 1rem;">{{ colaborador.nome }}</h2>
                <p></p>

                <div style="text-align: center; color: var(--secondary-color);">
                    <!-- Adicione mais informações do colaborador aqui -->
                    <strong>Cargo Atual |</strong> {{ colaborador.cargo }}
                </div>
                <p></p>

                <div style="text-align: center; color: var(--secondary-color);">
                    <!-- Adicione a data de contratação do colaborador -->
                    <strong>Data de Admissão |</strong> {{ colaborador.data_contratacao|date:"d/m/Y" }}
                </div>
                <p></p>

                <div style="text-align: center; color: var(--secondary-color);">
                    <!-- Adicione o hub do colaborador -->
                    <strong>Hub |</strong> {{ colaborador.hub }}
                </div>
            </div>

            <div class="chart-container">
                <h2>Resumo das Avaliações</h2>
                <canvas id="radarChart"></canvas>
            </div>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <h3>Pontualidade</h3>
                <div class="score">{{ media.pontualidade_media|floatformat:1 }}</div>
                <div class="trend {% if media.pontualidade_media >= 4.5 %}excellent{% elif media.pontualidade_media >= 3.5 %}good{% elif media.pontualidade_media >= 2.5 %}average{% else %}poor{% endif %}">
                    {% if media.pontualidade_media >= 4.5 %}
                        Excelente
                    {% elif media.pontualidade_media >= 3.5 %}
                        Bom
                    {% elif media.pontualidade_media >= 2.5 %}
                        Regular
                    {% else %}
                        Ruim
                    {% endif %}
                </div>
            </div>
            <div class="stat-card">
                <h3>Comunicação</h3>
                <div class="score">{{ media.comunicacao_media|floatformat:1 }}</div>
                <div class="trend {% if media.comunicacao_media >= 4.5 %}excellent{% elif media.comunicacao_media >= 3.5 %}good{% elif media.comunicacao_media >= 2.5 %}average{% else %}poor{% endif %}">
                    {% if media.comunicacao_media >= 4.5 %}
                        Excelente
                    {% elif media.comunicacao_media >= 3.5 %}
                        Bom
                    {% elif media.comunicacao_media >= 2.5 %}
                        Regular
                    {% else %}
                        Ruim
                    {% endif %}
                </div>
            </div>
            <div class="stat-card">
                <h3>Resolução de Problemas</h3>
                <div class="score">{{ media.resolucao_problemas_media|floatformat:1 }}</div>
                <div class="trend {% if media.resolucao_problemas_media >= 4.5 %}excellent{% elif media.resolucao_problemas_media >= 3.5 %}good{% elif media.resolucao_problemas_media >= 2.5 %}average{% else %}poor{% endif %}">
                    {% if media.resolucao_problemas_media >= 4.5 %}
                        Excelente
                    {% elif media.resolucao_problemas_media >= 3.5 %}
                        Bom
                    {% elif media.resolucao_problemas_media >= 2.5 %}
                        Regular
                    {% else %}
                        Ruim
                    {% endif %}
                </div>
            </div>
            <div class="stat-card">
                <h3>Postura Profissional</h3>
                <div class="score">{{ media.postura_profissional_media|floatformat:1 }}</div>
                <div class="trend {% if media.postura_profissional_media >= 4.5 %}excellent{% elif media.postura_profissional_media >= 3.5 %}good{% elif media.postura_profissional_media >= 2.5 %}average{% else %}poor{% endif %}">
                    {% if media.postura_profissional_media >= 4.5 %}
                        Excelente
                    {% elif media.postura_profissional_media >= 3.5 %}
                        Bom
                    {% elif media.postura_profissional_media >= 2.5 %}
                        Regular
                    {% else %}
                        Ruim
                    {% endif %}
                </div>
            </div>
            <div class="stat-card">
                <h3>Velocidade</h3>
                <div class="score">{{ media.velocidade_media|floatformat:1 }}</div>
                <div class="trend {% if media.velocidade_media >= 4.5 %}excellent{% elif media.velocidade_media >= 3.5 %}good{% elif media.velocidade_media >= 2.5 %}average{% else %}poor{% endif %}">
                    {% if media.velocidade_media >= 4.5 %}
                        Excelente
                    {% elif media.velocidade_media >= 3.5 %}
                        Bom
                    {% elif media.velocidade_media >= 2.5 %}
                        Regular
                    {% else %}
                        Ruim
                    {% endif %}
                </div>
            </div>
            <div class="stat-card">
                <h3>Precisão</h3>
                <div class="score">{{ media.precisao_media|floatformat:1 }}</div>
                <div class="trend {% if media.precisao_media >= 4.5 %}excellent{% elif media.precisao_media >= 3.5 %}good{% elif media.precisao_media >= 2.5 %}average{% else %}poor{% endif %}">
                    {% if media.precisao_media >= 4.5 %}
                        Excelente
                    {% elif media.precisao_media >= 3.5 %}
                        Bom
                    {% elif media.precisao_media >= 2.5 %}
                        Regular
                    {% else %}
                        Ruim
                    {% endif %}
                </div>
            </div>
            <div class="stat-card">
                <h3>Priorização das Tarefas</h3>
                <div class="score">{{ media.priorizacao_tarefas_media|floatformat:1 }}</div>
                <div class="trend {% if media.priorizacao_tarefas_media >= 4.5 %}excellent{% elif media.priorizacao_tarefas_media >= 3.5 %}good{% elif media.priorizacao_tarefas_media >= 2.5 %}average{% else %}poor{% endif %}">
                    {% if media.priorizacao_tarefas_media >= 4.5 %}
                        Excelente
                    {% elif media.priorizacao_tarefas_media >= 3.5 %}
                        Bom
                    {% elif media.priorizacao_tarefas_media >= 2.5 %}
                        Regular
                    {% else %}
                        Ruim
                    {% endif %}
                </div>
            </div>
            <div class="stat-card">
                <h3>Flexibilidade</h3>
                <div class="score">{{ media.flexibilidade_media|floatformat:1 }}</div>
                <div class="trend {% if media.flexibilidade_media >= 4.5 %}excellent{% elif media.flexibilidade_media >= 3.5 %}good{% elif media.flexibilidade_media >= 2.5 %}average{% else %}poor{% endif %}">
                    {% if media.flexibilidade_media >= 4.5 %}
                        Excelente
                    {% elif media.flexibilidade_media >= 3.5 %}
                        Bom
                    {% elif media.flexibilidade_media >= 2.5 %}
                        Regular
                    {% else %}
                        Ruim
                    {% endif %}
                </div>
            </div>
        </div>
        

        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Comentários e Avaliações</title>
            <style>
                /* Estilo geral para a lista de comentários */
                .comentarios-list {
                    list-style-type: none; /* Remove as bolinhas da lista */
                    padding: 0; /* Remove o padding */
                    margin: 20px auto; /* Centraliza a lista com margem automática */
                    max-width: 1500px; /* Largura máxima da lista */
                    width: 90%; /* Largura de 90% da tela para não ficar muito esticado */
                    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1); /* Sombra leve para a lista */
                    border-radius: 12px; /* Bordas arredondadas */
                    background: linear-gradient(135deg, #f9f9f9, #fff); /* Gradiente de fundo */
                    transition: background 0.3s ease; /* Transição suave ao mudar o fundo */
                }
        
                /* Efeito de hover para a lista de comentários */
                .comentarios-list:hover {
                    background: linear-gradient(135deg, #ffffff, #f1f1f1);
                }
        
                /* Estilo para cada comentário */
                .comentario {
                    background-color: #ffffff; /* Cor de fundo suave */
                    border: 1px solid #e0e0e0; /* Borda clara */
                    border-radius: 10px; /* Bordas arredondadas */
                    padding: 15px; /* Espaçamento interno */
                    margin: 15px; /* Espaço entre os comentários */
                    transition: transform 0.3s, box-shadow 0.3s, background-color 0.3s; /* Efeito de transição suave */
                    position: relative; /* Para posicionamento do efeito */
                    overflow: hidden; /* Para esconder o overflow */
                    display: flex; /* Utiliza flexbox para layout */
                    align-items: center; /* Alinha verticalmente os itens */
                }
        
                /* Efeito de hover para destacar o comentário ao passar o mouse */
                .comentario:hover {
                    transform: translateY(-5px); /* Leve elevação do comentário */
                    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3); /* Sombra mais intensa ao passar o mouse */
                    background-color: #f9f9f9; /* Mudança de fundo ao passar o mouse */
                }
        
                /* Efeito de animação no texto do comentário */
                .comentario-texto {
                    font-size: 16px; /* Tamanho da fonte */
                    color: #333; /* Cor do texto */
                    line-height: 1.5; /* Espaçamento entre linhas */
                    margin-left: 10px; /* Espaço à esquerda do texto */
                    margin-bottom: 8px; /* Espaço entre o texto e a data */
                    transition: color 0.3s ease; /* Transição suave na cor */
                }
        
                /* Mudança de cor do texto no hover */
                .comentario:hover .comentario-texto {
                    color: #007bff; /* Cor azul ao passar o mouse */
                }
        
                /* Estilo para a data do comentário */
                .comentario-data {
                    font-size: 14px; /* Tamanho menor para a data */
                    color: #666; /* Cor cinza para a data */
                    font-style: italic; /* Estilo itálico */
                    text-align: right; /* Alinha a data à direita */
                }
        
                /* Estilo para a imagem do usuário */
                .comentario-img {
                    width: 40px; /* Largura da imagem */
                    height: 40px; /* Altura da imagem */
                    border-radius: 50%; /* Imagem circular */
                    object-fit: cover; /* Cobre o espaço mantendo a proporção */
                }
        
                /* Estilo para o container do gráfico */
                .chart-container {
                    text-align: center; /* Centraliza o título do gráfico */
                    margin: 30px 0; /* Margem em cima e embaixo */
                }
                .social-btn {
                    background-color: #3b5998; /* Cor do Facebook */
                    color: white;
                    padding: 10px 20px;
                    font-size: 16px;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    gap: 8px; /* Espaço entre o ícone e o texto */
                    transition: background-color 0.3s ease;
                }
            
                .social-btn:hover {
                    background-color: #2d4373; /* Cor mais escura no hover */
                }
            
                .social-btn i {
                    font-size: 18px;
                }
            
                /* Posicionamento fixo no lado direito da tela */
                .social-btn {
                    position: fixed;
                    right: 20px; /* Distância da borda direita */
                    bottom: 20px; /* Distância da borda inferior */
                    z-index: 1000; /* Garante que o botão fique sobre outros elementos */
                }
            </style>
        </head>
        <body>
            <div class="chart-container">
                <h2>Evolução das Avaliações</h2>
                <canvas id="lineChart"></canvas>
            </div>


            <h3>Contentamento dos Restaurantes - Média das Avaliações por Loja</h3>

            <!-- Canvas para o gráfico -->
            <canvas id="barChartLoja"></canvas>

            <h3>Comentários sobre o Colaborador</h3>

            <!-- Botão personalizado para exibir ou ocultar comentários -->
            <button id="toggleCommentsButton" onclick="toggleComments()">Ver Comentários</button>
            
            <!-- Lista de comentários -->
            <div id="commentsSection" style="display: none;">
                <ul class="comentarios-list">
                    {% if avaliacoes %}
                        {% for avaliacao in avaliacoes %}
                            {% if avaliacao.comentario %}
                                <li class="comentario">
                                    <img src="{% static 'assets/img/Perfil1.jpg' %}" alt="Usuário" class="comentario-img"> <!-- Imagem do usuário -->
                                    <div class="comentario-conteudo">
                                        <p class="comentario-texto">{{ avaliacao.comentario }}</p>
                                        <span class="comentario-data">{{ avaliacao.data }}</span> <!-- Se você tiver uma data -->
                                    </div>
                                </li>
                            {% endif %}
                        {% endfor %}
                    {% else %}
                        <li class="comentario">
                            <p class="comentario-texto">Nenhum comentário disponível.</p>
                        </li>
                    {% endif %}
                </ul>
            </div>
            
        </body>
        
    <script>
        // Dados para o gráfico radar
        const radarData = {
            labels: [
                'Pontualidade',
                'Organização',
                'Comunicação',
                'Resolução de Problemas',
                'Precisão',
                'Velocidade',
                'Conhecimento de Ferramentas',
                'Flexibilidade',
                'Postura Profissional',
                'Priorização de Tarefas'
            ],
            datasets: [{
                label: 'Avaliação Atual',
                data: [
                    {{ media.pontualidade_media }},
                    {{ media.organizacao_media }},
                    {{ media.comunicacao_media }},
                    {{ media.resolucao_problemas_media }},
                    {{ media.precisao_media }},
                    {{ media.velocidade_media }},
                    {{ media.conhecimento_ferramentas_media }},
                    {{ media.flexibilidade_media }},
                    {{ media.postura_profissional_media }},
                    {{ media.priorizacao_tarefas_media }}
                ],
                fill: true,
                backgroundColor: 'rgba(37, 99, 235, 0.2)',
                borderColor: 'rgb(37, 99, 235)',
                pointBackgroundColor: 'rgb(37, 99, 235)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgb(37, 99, 235)'
            }]
        };

        // Configuração do gráfico radar
        const radarConfig = {
            type: 'radar',
            data: radarData,
            options: {
                elements: {
                    line: {
                        borderWidth: 3
                    }
                },
                scales: {
                    r: {
                        angleLines: {
                            display: true
                        },
                        suggestedMin: 0,
                        suggestedMax: 5
                    }
                }
            }
        };

        // Renderizar gráfico radar
        const radarChart = new Chart(
            document.getElementById('radarChart'),
            radarConfig
        );

        const labels = [
        {% for avaliacao in avaliacoes %}
            "{{ avaliacao.data|date:"F" }}",
        {% endfor %}
    ];

    const dataValues = [
        {% for nota in notas_evolucao %}
            {{ nota }},
        {% endfor %}
    ];

    // Configuração dos dados para o gráfico de linha
    const lineData = {
        labels: labels,
        datasets: [{
            label: 'Evolução da Avaliação',
            data: dataValues,
            fill: false,
            borderColor: 'rgb(75, 192, 192)',
            tension: 0.1
        }]
    };

    // Configuração do gráfico de linha
    const lineConfig = {
        type: 'line',
        data: lineData,
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    };

    // Renderizar gráfico de linha
    const lineChart = new Chart(
        document.getElementById('lineChart'),
        lineConfig
    );

    // Extraindo os dados de lojas e suas médias do template
    const lojas = [
    {% for loja in medias_por_loja %}
        "{{ loja.loja }}",  // Nome da loja
    {% endfor %}
    ];

    const mediasLoja = [
    {% for loja in medias_por_loja %}
        {{ loja.media_loja|floatformat:2 }},  // Média das avaliações por loja
    {% endfor %}
    ];

    // Configuração dos dados para o gráfico de barras por loja
    const barDataLoja = {
    labels: lojas,  // Labels (nomes das lojas)
    datasets: [{
        label: 'Média das Avaliações por Loja',
        data: mediasLoja,  // Dados (média das avaliações por loja)
        backgroundColor: 'rgba(153, 102, 255, 0.2)',  // Cor de fundo das barras
        borderColor: 'rgb(153, 102, 255)',  // Cor da borda das barras
        borderWidth: 1
    }]
    };

    // Configuração do gráfico de barras
    const barConfigLoja = {
    type: 'bar',
    data: barDataLoja,
    options: {
        responsive: true,
        scales: {
            y: {
                beginAtZero: true  // Inicia o eixo Y do gráfico em 0
            }
        }
    }
    };

    // Renderiza o gráfico
    const barChartLoja = new Chart(
    document.getElementById('barChartLoja'),
    barConfigLoja
    );

    function toggleComments() {
        var commentsSection = document.getElementById('commentsSection');
        var toggleButton = document.getElementById('toggleCommentsButton');
        
        if (commentsSection.style.display === 'none') {
            commentsSection.style.display = 'block';
            toggleButton.textContent = 'Ocultar Comentários';
        } else {
            commentsSection.style.display = 'none';
            toggleButton.textContent = 'Ver Comentários';
        }
    }
    </script>

</body>
</html>
