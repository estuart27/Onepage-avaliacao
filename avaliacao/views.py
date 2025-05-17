from django.shortcuts import render, redirect, get_object_or_404
from .models import Colaborador, Avaliacao,Hub,Avaliacao_Restaurante
from .forms import AvaliacaoForm,AvaliacaoMensageiroForm
from django.db.models import Avg, Count
from .utils import analizar_partida,gerar_feedback_restaurante,relatorio  # Certifique-se de que a função resposta_bot está no arquivo correto
from datetime import datetime, timedelta
from django.core.paginator import Paginator
from django.db.models.functions import Coalesce
from django.db.models import OuterRef, Count, Avg, Value, FloatField, Subquery, F, Case, When
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from django.conf import settings


def home(request):
    # Verifica se o código já foi validado na sessão
    if not request.session.get('codigo_acesso_validado'):
        return render(request, 'avaliacao/codigo_acesso.html')
    
    # Subqueries para contar o total de avaliações (não avaliadores únicos)
    colaborador_reviews_count_subquery = Colaborador.objects.filter(
        pk=OuterRef('pk')
    ).annotate(
        total_avaliacoes_colaborador=Count('avaliacoes')
    ).values('total_avaliacoes_colaborador')

    restaurante_reviews_count_subquery = Colaborador.objects.filter(
        pk=OuterRef('pk')
    ).annotate(
        total_avaliacoes_restaurante=Count('avaliacoes_restaurantes')
    ).values('total_avaliacoes_restaurante')

    # Obter opções de cargo e hub distintos
    cargos = Colaborador.objects.values_list('cargo', flat=True).distinct()
    hubs = Hub.objects.all()

    # Realizar join para combinar avaliações de colaboradores e restaurante
    colaboradores = Colaborador.objects.annotate(
        total_avaliacoes_colaborador=Coalesce(Subquery(colaborador_reviews_count_subquery), Value(0)),
        total_avaliacoes_restaurante=Coalesce(Subquery(restaurante_reviews_count_subquery), Value(0)),
        media_avaliacao_colaborador=Coalesce(Avg('avaliacoes__nota'), Value(0.0), output_field=FloatField()),
        media_avaliacao_restaurante=Coalesce(Avg('avaliacoes_restaurantes__nota'), Value(0.0), output_field=FloatField()),
    ).annotate(
        total_avaliacoes_total=F('total_avaliacoes_colaborador') + F('total_avaliacoes_restaurante'),
        media_avaliacao_total=Coalesce(
            Case(
                When(total_avaliacoes_total=0, then=Value(0.0)),
                default=(
                    (F('media_avaliacao_colaborador') * F('total_avaliacoes_colaborador') + 
                     F('media_avaliacao_restaurante') * F('total_avaliacoes_restaurante')) / 
                    F('total_avaliacoes_total')
                ),
                output_field=FloatField()
            ),
            Value(0.0),
            output_field=FloatField()
        )
    ).order_by('id')
    
    cargo_selecionado = request.GET.get('cargo')
    hub_selecionado = request.GET.get('hub')
    search = request.GET.get('search', '')

    # Aplicar filtros
    if cargo_selecionado:
        colaboradores = colaboradores.filter(cargo=cargo_selecionado)

    if hub_selecionado:
        colaboradores = colaboradores.filter(hub_id=hub_selecionado)

    if search:
        colaboradores = colaboradores.filter(nome__icontains=search)

    # Paginação
    paginator = Paginator(colaboradores, 9)
    page_number = request.GET.get('page')
    colaboradores_paginated = paginator.get_page(page_number)

    context = {
        'colaboradores': colaboradores_paginated,
        'cargos': cargos,
        'hubs': hubs,
        'request': request
    }
    return render(request, 'avaliacao/home.html', context)

def validar_codigo(request):
    if request.method == 'POST':
        codigo_inserido = request.POST.get('codigo')

        if codigo_inserido == settings.CODIGO_CORRETO:
            request.session['codigo_acesso_validado'] = True
            return redirect('home')  # ou o nome da sua URL
        else:
            return render(request, 'avaliacao/codigo_acesso.html', {'erro': 'Código incorreto.'})


def classificar_colaborador(media_geral):
    if media_geral is None:
        return "Sem avaliações suficientes"
    elif media_geral >= 4.6:
        return "Sujeito a promoção"
    elif media_geral >= 4.0:
        return "Sujeito a bonificação"
    elif media_geral >= 3.5:
        return "Sujeito a melhorias"
    elif media_geral >= 3.0:
        return "Sujeito a estagnação"
    else:
        return "Sujeito a demissão"


# from datetime import datetime, timedelta
# # ...existing code...

# def perfil_colaborador(request, colaborador_id):
#     if not request.user.is_superuser:
#         return redirect('/admin/login/?next=' + request.path)
#     colaborador = get_object_or_404(Colaborador, id=colaborador_id)
    
#     # Obtém as avaliações relacionadas ao colaborador
#     avaliacoes = colaborador.avaliacoes.all().order_by('-data')

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

#     # --- NOVO: filtra avaliações dos últimos 2 meses para a classificação ---
#     dois_meses_atras = datetime.now() - timedelta(days=60)
#     avaliacoes_2m = avaliacoes.filter(data__gte=dois_meses_atras)
#     media_geral = avaliacoes_2m.aggregate(media_geral=Avg('nota'))['media_geral']
#     # ------------------------------------------------------------------------

#     total_avaliacoes = avaliacoes.count()

#     # Extrai notas e datas para a evolução das avaliações
#     notas_evolucao = [avaliacao.nota for avaliacao in avaliacoes]
#     datas_evolucao = [avaliacao.data.strftime('%B') for avaliacao in avaliacoes]

#     # Calcula a média por loja
#     medias_por_loja = avaliacoes.values('loja').annotate(
#         media_loja=Avg('nota')
#     )

#     classificacao = classificar_colaborador(media_geral)

#     # Passa os dados para o template
#     return render(request, 'avaliacao/perfil_colaborador.html', {
#         'colaborador': colaborador,
#         'media': media,
#         'media_geral': media_geral,
#         'total_avaliacoes': total_avaliacoes,
#         'avaliacoes': avaliacoes,
#         'notas_evolucao': notas_evolucao,
#         'datas_evolucao': datas_evolucao,
#         'medias_por_loja': medias_por_loja,
#         'classificacao': classificacao,
#     })


def perfil_colaborador(request, colaborador_id):
    if not request.user.is_superuser:
        return redirect('/admin/login/?next=' + request.path)
    colaborador = get_object_or_404(Colaborador, id=colaborador_id)
    
    # Obtém as avaliações relacionadas ao colaborador
    avaliacoes = colaborador.avaliacoes.all().order_by('-data')

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

     # --- NOVO: filtra avaliações dos últimos 2 meses para a classificação ---
    dois_meses_atras = datetime.now() - timedelta(days=60)
    avaliacoes_2m = avaliacoes.filter(data__gte=dois_meses_atras)
    media_mes = avaliacoes_2m.aggregate(media_geral=Avg('nota'))['media_geral']

    # Extrai notas e datas para a evolução das avaliações
    notas_evolucao = [avaliacao.nota for avaliacao in avaliacoes]
    datas_evolucao = [avaliacao.data.strftime('%B') for avaliacao in avaliacoes]

    # Calcula a média por loja
    medias_por_loja = avaliacoes.values('loja').annotate(
        media_loja=Avg('nota')
    )

    classificacao = classificar_colaborador(media_mes)

    # Passa os dados para o template
    return render(request, 'avaliacao/perfil_colaborador.html', {
        'colaborador': colaborador,
        'media': media,
        'media_geral': media_geral,
        'total_avaliacoes': total_avaliacoes,
        'avaliacoes': avaliacoes,
        'notas_evolucao': notas_evolucao,
        'datas_evolucao': datas_evolucao,
        'medias_por_loja': medias_por_loja,  # Passa as médias por loja
        'classificacao': classificacao,  # <- aqui

    })



def perfil_colaborador_restaurante(request, colaborador_id):
    # Verifica se o usuário é um superusuário
    if not request.user.is_superuser:
        return redirect('/admin/login/?next=' + request.path)
    
    # Obtém o colaborador ou retorna 404 se não existir
    colaborador = get_object_or_404(Colaborador, id=colaborador_id)
    
    # Obtém as avaliações de restaurante relacionadas ao colaborador
    avaliacoes = colaborador.avaliacoes_restaurantes.all().order_by('-data')

    # Calcula a média para cada critério de avaliação
    media = {
        'rapidez_atendimento_media': avaliacoes.aggregate(Avg('rapidez_atendimento'))['rapidez_atendimento__avg'] or 0,
        'eficiencia_resolucao_media': avaliacoes.aggregate(Avg('eficiencia_resolucao'))['eficiencia_resolucao__avg'] or 0,
        'clareza_comunicacao_media': avaliacoes.aggregate(Avg('clareza_comunicacao'))['clareza_comunicacao__avg'] or 0,
        'profissionalismo_media': avaliacoes.aggregate(Avg('profissionalismo'))['profissionalismo__avg'] or 0,
        'suporte_gestao_pedidos_media': avaliacoes.aggregate(Avg('suporte_gestao_pedidos'))['suporte_gestao_pedidos__avg'] or 0,
        'proatividade_media': avaliacoes.aggregate(Avg('proatividade'))['proatividade__avg'] or 0,
        'disponibilidade_media': avaliacoes.aggregate(Avg('disponibilidade'))['disponibilidade__avg'] or 0,
        'satisfacao_geral_media': avaliacoes.aggregate(Avg('satisfacao_geral'))['satisfacao_geral__avg'] or 0,
    }

    # Calcula a média geral de todas as notas de avaliação
    media_geral = avaliacoes.aggregate(media_geral=Avg('nota'))['media_geral'] or 0
    total_avaliacoes = avaliacoes.count()

    # Extrai notas e datas para a evolução das avaliações
    notas_evolucao = [avaliacao.nota for avaliacao in avaliacoes]
    datas_evolucao = [avaliacao.data.strftime('%B') for avaliacao in avaliacoes]

    # Calcula a média por loja
    medias_por_loja = avaliacoes.values('loja').annotate(
        media_loja=Avg('nota')
    )

    # Passa os dados para o template
    context = {
        'colaborador': colaborador,
        'media': media,
        'media_geral': media_geral,
        'total_avaliacoes': total_avaliacoes,
        'avaliacoes': avaliacoes,
        'notas_evolucao': notas_evolucao,
        'datas_evolucao': datas_evolucao,
        'medias_por_loja': medias_por_loja
    }
    
    return render(request, 'avaliacao/perfil_colaborador_restaurante.html', context)


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


def feedback_colaborador_restaurante(request, colaborador_id):
    try:
        colaborador = get_object_or_404(Colaborador, id=colaborador_id)
        data_um_mes_atras = datetime.now() - timedelta(days=30)

        avaliacoes = colaborador.avaliacoes_restaurantes.filter(data__gte=data_um_mes_atras).order_by('-data')
        comentarios_mais_recentes = [avaliacao.comentario for avaliacao in avaliacoes if avaliacao.comentario]

        if not avaliacoes:
            dados_avaliacao = {
                'nome': colaborador.nome,
                'rapidez_atendimento': 0,
                'eficiencia_resolucao': 0,
                'clareza_comunicacao': 0,
                'profissionalismo': 0,
                'suporte_gestao_pedidos': 0,
                'proatividade': 0,
                'disponibilidade': 0,
                'satisfacao_geral': 0,
            }
        else:
            dados_avaliacao = {
                'nome': colaborador.nome,
                'rapidez_atendimento': sum([a.rapidez_atendimento for a in avaliacoes]) / len(avaliacoes),
                'eficiencia_resolucao': sum([a.eficiencia_resolucao for a in avaliacoes]) / len(avaliacoes),
                'clareza_comunicacao': sum([a.clareza_comunicacao for a in avaliacoes]) / len(avaliacoes),
                'profissionalismo': sum([a.profissionalismo for a in avaliacoes]) / len(avaliacoes),
                'suporte_gestao_pedidos': sum([a.suporte_gestao_pedidos for a in avaliacoes]) / len(avaliacoes),
                'proatividade': sum([a.proatividade for a in avaliacoes]) / len(avaliacoes),
                'disponibilidade': sum([a.disponibilidade for a in avaliacoes]) / len(avaliacoes),
                'satisfacao_geral': sum([a.satisfacao_geral for a in avaliacoes]) / len(avaliacoes),
                'comentario': comentarios_mais_recentes,
            }

        feedback = gerar_feedback_restaurante(dados_avaliacao)

        return render(request, 'avaliacao/feedback_restaurante.html', {
            'feedback': feedback,
            'colaborador': colaborador,
            'comentarios': comentarios_mais_recentes
        })

    except Colaborador.DoesNotExist:
        return render(request, 'erro.html', {'message': 'Colaborador não encontrado.'})



# Página de avaliação do colaborador
def avaliar_colaborador(request, colaborador_id):
    colaborador = get_object_or_404(Colaborador, id=colaborador_id)
    
    if request.method == 'POST':
        form = AvaliacaoForm(request.POST)
        if form.is_valid():
            avaliacao = form.save(commit=False)
            avaliacao.colaborador = colaborador
            avaliacao.save()
            # Renderiza a página de confirmação
            return render(request, 'avaliacao/avaliacao_enviada.html', {'colaborador': colaborador})
    else:
        form = AvaliacaoForm()
    
    return render(request, 'avaliacao/avaliar_colaborador.html', {'form': form, 'colaborador': colaborador})



def avaliacao_restaurante(request, colaborador_id):
    colaborador = get_object_or_404(Colaborador, id=colaborador_id)
    
    if request.method == 'POST':
        form = AvaliacaoMensageiroForm(request.POST)
        if form.is_valid():
            avaliacao = form.save(commit=False)
            avaliacao.colaborador = colaborador
            avaliacao.save()
            # Renderiza a página de confirmação
            return render(request, 'avaliacao/avaliacao_enviada.html', {'colaborador': colaborador})
    else:
        form = AvaliacaoMensageiroForm()
    
    return render(request, 'avaliacao/avaliacao_restaurante.html', {'form': form, 'colaborador': colaborador})


def relatorio_op(request):
    # Verifica se o usuário é um superusuário
    if not request.user.is_superuser:
        return redirect('/admin/login/?next=' + request.path)
    
    return render(request, 'avaliacao/relatorio.html')


@csrf_exempt
@require_POST
def generate_report(request):
    try:
        # Parse JSON data from request
        data = json.loads(request.body)
        feedback = data.get('feedback', '')
        prompt = data.get('prompt', '')
        
        # Call the relatorio function
        result = relatorio(feedback, prompt)
        
        # Return the report
        return JsonResponse({'report': result})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

