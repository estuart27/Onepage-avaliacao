from django.shortcuts import render, redirect, get_object_or_404
from .models import Colaborador, Avaliacao
from .forms import AvaliacaoForm
from django.db.models import Avg, Count

def home(request):
    # Obter opções de cargo e hub distintos
    cargos = Colaborador.objects.values_list('cargo', flat=True).distinct()
    hubs = Colaborador.objects.values_list('hub', flat=True).distinct()

    # Obter todos os colaboradores e aplicar filtros, se fornecidos
    colaboradores = Colaborador.objects.all().annotate(
        media_avaliacao=Avg('avaliacoes__nota'),
        total_avaliacoes=Count('avaliacoes')
    )
    cargo_selecionado = request.GET.get('cargo')
    hub_selecionado = request.GET.get('hub')

    if cargo_selecionado:
        colaboradores = colaboradores.filter(cargo=cargo_selecionado)
    if hub_selecionado:
        colaboradores = colaboradores.filter(hub=hub_selecionado)

    context = {
        'colaboradores': colaboradores,
        'cargos': cargos,
        'hubs': hubs,
    }
    return render(request, 'avaliacao/home.html', context)

# Página de avaliação do colaborador
def avaliar_colaborador(request, colaborador_id):
    colaborador = get_object_or_404(Colaborador, id=colaborador_id)
    
    if request.method == 'POST':
        form = AvaliacaoForm(request.POST)
        if form.is_valid():
            avaliacao = form.save(commit=False)
            avaliacao.colaborador = colaborador
            avaliacao.save()
            return redirect('perfil_colaborador', colaborador_id=colaborador_id)
    else:
        form = AvaliacaoForm()
    
    return render(request, 'avaliacao/avaliar_colaborador.html', {'form': form, 'colaborador': colaborador})


# def perfil_colaborador(request, colaborador_id):
#     colaborador = get_object_or_404(Colaborador, id=colaborador_id)
    
#     # Obtém as avaliações relacionadas ao colaborador
#     avaliacoes = colaborador.avaliacoes.all().order_by('data')

#     # Calcula a média para cada critério de avaliação e a média geral
#     media = avaliacoes.aggregate(
#         pontualidade_media=Avg('pontualidade'),
#         organizacao_media=Avg('organizacao'),
#         comunicacao_media=Avg('comunicacao'),
#         resolucao_problemas_media=Avg('resolucao_problemas'),
#         precisao_media=Avg('precisao'),
#         velocidade_media=Avg('velocidade'),
#         conhecimento_ferramentas_media=Avg('conhecimento_ferramentas'),
#         flexibilidade_media=Avg('flexibilidade'),
#         postura_profissional_media=Avg('postura_profissional'),
#         priorizacao_tarefas_media=Avg('priorizacao_tarefas')
#     )

#     # Calcula a média geral de todas as notas de avaliação
#     media_geral = avaliacoes.aggregate(media_geral=Avg('nota'))['media_geral']
#     total_avaliacoes = avaliacoes.count()

#     # Extraia notas e datas para a evolução das avaliações (opcional para gráficos)
#     notas_evolucao = [avaliacao.nota for avaliacao in avaliacoes]
#     datas_evolucao = [avaliacao.data.strftime('%B') for avaliacao in avaliacoes]

#     # Calcular a média das avaliações por avaliador
#     medias_por_avaliador = avaliacoes.values('avaliador').annotate(
#         media_avaliador=Avg('nota')
#     )

#     # Passa os dados para o template
#     return render(request, 'avaliacao/perfil_colaborador.html', {
#         'colaborador': colaborador,
#         'media': media,
#         'media_geral': media_geral,
#         'total_avaliacoes': total_avaliacoes,
#         'avaliacoes': avaliacoes,
#         'notas_evolucao': notas_evolucao,
#         'datas_evolucao': datas_evolucao,
#         'medias_por_avaliador': medias_por_avaliador  # Adiciona as médias por avaliador
#     })

from django.db.models import Avg

def perfil_colaborador(request, colaborador_id):
    colaborador = get_object_or_404(Colaborador, id=colaborador_id)
    
    # Obtém as avaliações relacionadas ao colaborador
    avaliacoes = colaborador.avaliacoes.all().order_by('data')

    # Calcula a média para cada critério de avaliação e a média geral
    media = avaliacoes.aggregate(
        pontualidade_media=Avg('pontualidade'),
        organizacao_media=Avg('organizacao'),
        comunicacao_media=Avg('comunicacao'),
        resolucao_problemas_media=Avg('resolucao_problemas'),
        precisao_media=Avg('precisao'),
        velocidade_media=Avg('velocidade'),
        conhecimento_ferramentas_media=Avg('conhecimento_ferramentas'),
        flexibilidade_media=Avg('flexibilidade'),
        postura_profissional_media=Avg('postura_profissional'),
        priorizacao_tarefas_media=Avg('priorizacao_tarefas')
    )

    # Calcula a média geral de todas as notas de avaliação
    media_geral = avaliacoes.aggregate(media_geral=Avg('nota'))['media_geral']
    total_avaliacoes = avaliacoes.count()

    # Extrai notas e datas para a evolução das avaliações
    notas_evolucao = [avaliacao.nota for avaliacao in avaliacoes]
    datas_evolucao = [avaliacao.data.strftime('%B') for avaliacao in avaliacoes]

    # Calcula a média por loja
    medias_por_loja = avaliacoes.values('loja').annotate(
        media_loja=Avg('nota')
    )

    # Passa os dados para o template
    return render(request, 'avaliacao/perfil_colaborador.html', {
        'colaborador': colaborador,
        'media': media,
        'media_geral': media_geral,
        'total_avaliacoes': total_avaliacoes,
        'avaliacoes': avaliacoes,
        'notas_evolucao': notas_evolucao,
        'datas_evolucao': datas_evolucao,
        'medias_por_loja': medias_por_loja  # Passa as médias por loja
    })



















# Página de perfil do colaborador que exibe a média das avaliações
# def perfil_colaborador(request, colaborador_id):
#     colaborador = get_object_or_404(Colaborador, id=colaborador_id)
    
#     # Obtém as avaliações relacionadas ao colaborador
#     avaliacoes = colaborador.avaliacoes.all().order_by('data')

#     # Calcula a média para cada critério de avaliação e a média geral
#     media = avaliacoes.aggregate(
#         pontualidade_media=Avg('pontualidade'),
#         organizacao_media=Avg('organizacao'),
#         comunicacao_media=Avg('comunicacao'),
#         resolucao_problemas_media=Avg('resolucao_problemas'),
#         precisao_media=Avg('precisao'),
#         velocidade_media=Avg('velocidade'),
#         conhecimento_ferramentas_media=Avg('conhecimento_ferramentas'),
#         flexibilidade_media=Avg('flexibilidade'),
#         postura_profissional_media=Avg('postura_profissional'),
#         priorizacao_tarefas_media=Avg('priorizacao_tarefas')
#     )

#     # Calcula a média geral de todas as notas de avaliação
#     media_geral = avaliacoes.aggregate(media_geral=Avg('nota'))['media_geral']
#     total_avaliacoes = avaliacoes.count()

#     # Extraia notas e datas para a evolução das avaliações (opcional para gráficos)
#     notas_evolucao = [avaliacao.nota for avaliacao in avaliacoes]
#     datas_evolucao = [avaliacao.data.strftime('%B') for avaliacao in avaliacoes]

#     # Passa os dados para o template
#     return render(request, 'avaliacao/perfil_colaborador.html', {
#         'colaborador': colaborador,
#         'media': media,
#         'media_geral': media_geral,         # Média geral das avaliações
#         'total_avaliacoes': total_avaliacoes,  # Total de avaliações
#         'avaliacoes': avaliacoes,
#         'notas_evolucao': notas_evolucao,    # Lista de notas para o gráfico
#         'datas_evolucao': datas_evolucao     # Datas formatadas para o gráfico
#     })



# from django.shortcuts import render, redirect, get_object_or_404
# from .models import Colaborador, Avaliacao
# from .forms import AvaliacaoForm
# from django.db.models import Avg

# from django.shortcuts import render
# from .models import Colaborador

# def home(request):
#     # Obter opções de cargo e hub distintos
#     cargos = Colaborador.objects.values_list('cargo', flat=True).distinct()
#     hubs = Colaborador.objects.values_list('hub', flat=True).distinct()

#     # Obter todos os colaboradores e aplicar filtros, se fornecidos
#     colaboradores = Colaborador.objects.all()
#     cargo_selecionado = request.GET.get('cargo')
#     hub_selecionado = request.GET.get('hub')

#     if cargo_selecionado:
#         colaboradores = colaboradores.filter(cargo=cargo_selecionado)
#     if hub_selecionado:
#         colaboradores = colaboradores.filter(hub=hub_selecionado)

#     context = {
#         'colaboradores': colaboradores,
#         'cargos': cargos,
#         'hubs': hubs,
#     }
#     return render(request, 'avaliacao/home.html', context)


# # Página de avaliação do colaborador
# def avaliar_colaborador(request, colaborador_id):
#     colaborador = Colaborador.objects.get(id=colaborador_id)
    
#     if request.method == 'POST':
#         form = AvaliacaoForm(request.POST)
#         if form.is_valid():
#             avaliacao = form.save(commit=False)
#             avaliacao.colaborador = colaborador
#             avaliacao.save()
#             return redirect('perfil_colaborador', colaborador_id=colaborador_id)
#     else:
#         form = AvaliacaoForm()
    
#     return render(request, 'avaliacao/avaliar_colaborador.html', {'form': form, 'colaborador': colaborador})

# # Página de perfil do colaborador que exibe a média das avaliações
# from django.db.models import Avg
# from django.shortcuts import render, get_object_or_404
# from .models import Colaborador

# def perfil_colaborador(request, colaborador_id):
#     colaborador = get_object_or_404(Colaborador, id=colaborador_id)
    
#     # Obtém as avaliações relacionadas ao colaborador
#     avaliacoes = colaborador.avaliacoes.all().order_by('data')  # Ordena por data

#     # Calcula a média das avaliações
#     media = avaliacoes.aggregate(
#         pontualidade_media=Avg('pontualidade'),
#         organizacao_media=Avg('organizacao'),
#         comunicacao_media=Avg('comunicacao'),
#         resolucao_problemas_media=Avg('resolucao_problemas'),
#         precisao_media=Avg('precisao'),
#         velocidade_media=Avg('velocidade'),
#         conhecimento_ferramentas_media=Avg('conhecimento_ferramentas'),
#         flexibilidade_media=Avg('flexibilidade'),
#         postura_profissional_media=Avg('postura_profissional'),
#         priorizacao_tarefas_media=Avg('priorizacao_tarefas')
#     )

#     # Extraia notas e datas para a evolução das avaliações
#     notas_evolucao = [avaliacao.pontualidade for avaliacao in avaliacoes]  # Ajustado para pegar a média de um atributo, como 'pontualidade'
#     datas_evolucao = [avaliacao.data.strftime('%B') for avaliacao in avaliacoes]  # Formato de mês

#     # Passa os dados para o template
#     return render(request, 'avaliacao/perfil_colaborador.html', {
#         'colaborador': colaborador,
#         'media': media,
#         'avaliacoes': avaliacoes,
#         'notas_evolucao': notas_evolucao,  # Lista de notas para o gráfico
#         'datas_evolucao': datas_evolucao   # Datas formatadas para o gráfico
#     }) 


