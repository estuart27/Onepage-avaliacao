from django.shortcuts import render, redirect, get_object_or_404
from .models import Colaborador, Avaliacao
from .forms import AvaliacaoForm
from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404
from .utils import analizar_partida  # Certifique-se de que a função resposta_bot está no arquivo correto
from datetime import datetime, timedelta



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
            # return redirect('perfil_colaborador', colaborador_id=colaborador_id)
            # return redirect('avaliacao/home.html')
            return render(request, 'avaliacao/avaliacao_enviada.html', {'colaborador_id': colaborador_id})

    else:
        form = AvaliacaoForm()
    
    return render(request, 'avaliacao/avaliar_colaborador.html', {'form': form, 'colaborador': colaborador})


def perfil_colaborador(request, colaborador_id):
    if not request.user.is_superuser:
        return redirect('/admin/login/?next=' + request.path)
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

def feedback_colaborador(request, colaborador_id):
    try:        
        # Obtém o colaborador com o ID fornecido
        colaborador = Colaborador.objects.get(id=colaborador_id)

        # Calcula a data de um mês atrás
        data_um_mes_atras = datetime.now() - timedelta(days=30)

        # Obtemos todas as avaliações do colaborador que são do último mês
        avaliacoes = Avaliacao.objects.filter(colaborador=colaborador, data__gte=data_um_mes_atras).order_by('-data')

        # Pega os comentários do último mês
        comentarios_mais_recentes = [avaliacao.comentario for avaliacao in avaliacoes if avaliacao.comentario]



        if not avaliacoes:
            # Caso não haja avaliações, definimos valores padrão para a média
            dados_avaliacao = {
                'nome': colaborador.nome,
                'pontualidade': 0,
                'organizacao': 0,
                'comunicacao': 0,
                'resolucao_problemas': 0,
                'precisao': 0,
                'velocidade': 0,
                'conhecimento_ferramentas': 0,
                'flexibilidade': 0,
                'postura_profissional': 0,
                'priorizacao_tarefas': 0
            }
        else:
            # Calcula a média das avaliações para o colaborador
            dados_avaliacao = {
                'nome': colaborador.nome,
                'pontualidade': sum([a.pontualidade for a in avaliacoes]) / len(avaliacoes),
                'organizacao': sum([a.organizacao for a in avaliacoes]) / len(avaliacoes),
                'comunicacao': sum([a.comunicacao for a in avaliacoes]) / len(avaliacoes),
                'resolucao_problemas': sum([a.resolucao_problemas for a in avaliacoes]) / len(avaliacoes),
                'precisao': sum([a.precisao for a in avaliacoes]) / len(avaliacoes),
                'velocidade': sum([a.velocidade for a in avaliacoes]) / len(avaliacoes),
                'conhecimento_ferramentas': sum([a.conhecimento_ferramentas for a in avaliacoes]) / len(avaliacoes),
                'flexibilidade': sum([a.flexibilidade for a in avaliacoes]) / len(avaliacoes),
                'postura_profissional': sum([a.postura_profissional for a in avaliacoes]) / len(avaliacoes),
                'priorizacao_tarefas': sum([a.priorizacao_tarefas for a in avaliacoes]) / len(avaliacoes),
                'comentario': comentarios_mais_recentes,
            }
        
        
        # Chama a função que gera o feedback com base nas avaliações
        feedback = analizar_partida(dados_avaliacao)

        # Renderiza a resposta no template
        return render(request, 'avaliacao/feedback.html', {'feedback': feedback, 'colaborador': colaborador, 'comentarios': comentarios_mais_recentes})
    
    except Colaborador.DoesNotExist:
        # Caso o colaborador não exista, podemos tratar o erro de forma apropriada
        return render(request, 'erro.html', {'message': 'Colaborador não encontrado.'})








