# avaliacao/views.py

from django.shortcuts import render, redirect, get_object_or_404
# Imports atualizados
from .models import Colaborador, Hub, AvaliacaoMensageiro, AvaliacaoAssistente,Medalha, SugestaoMedalha
# Imports atualizados
from .forms import AvaliacaoRestauranteForm, AvaliacaoMensageiroForm, AvaliacaoAssistenteForm
from .utils import analizar_partida,relatorio
from datetime import datetime, timedelta
from django.core.paginator import Paginator
from django.db.models.functions import Coalesce
from django.db.models import OuterRef, Count, Avg, Value, FloatField, Subquery, F, Case, When
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from django.conf import settings
from django.utils import timezone


def home(request):
    if not request.session.get('codigo_acesso_validado'):
        return render(request, 'avaliacao/codigo_acesso.html')
    
    cargos = Colaborador.objects.values_list('cargo', flat=True).distinct()
    hubs = Hub.objects.all()

    colaboradores = Colaborador.objects.annotate(
        # Contagem de avaliações de gestor (Mensageiro + Assistente)
        total_avaliacoes_mensageiro=Count('avaliacaomensageiro', distinct=True),
        total_avaliacoes_assistente=Count('avaliacaoassistente', distinct=True),
        
        # --- CORREÇÃO AQUI ---
        # Contagem de avaliações de restaurante
        total_avaliacoes_restaurante=Count('avaliacoes_recebidas_restaurantes', distinct=True), 

        # Médias de gestor (usando nota_final)
        media_mensageiro=Coalesce(Avg('avaliacaomensageiro__nota_final'), Value(0.0), output_field=FloatField()),
        media_assistente=Coalesce(Avg('avaliacaoassistente__nota_final'), Value(0.0), output_field=FloatField()),
        
        # --- CORREÇÃO AQUI ---
        # Média de restaurante (usando nota_final)
        media_avaliacao_restaurante=Coalesce(Avg('avaliacoes_recebidas_restaurantes__nota_final'), Value(0.0), output_field=FloatField()),
    
    ).annotate(
        # Soma do total de avaliações de gestor
        total_avaliacoes_colaborador=F('total_avaliacoes_mensageiro') + F('total_avaliacoes_assistente'),
        
        # Cálculo da média ponderada de GESTOR
        media_avaliacao_colaborador=Case(
            When(total_avaliacoes_colaborador=0, then=Value(0.0)),
            default=(
                (F('media_mensageiro') * F('total_avaliacoes_mensageiro') + 
                 F('media_assistente') * F('total_avaliacoes_assistente')) / 
                F('total_avaliacoes_colaborador')
            ),
            output_field=FloatField()
        ),

    ).annotate(
        # Cálculo da média GERAL (Gestor + Restaurante)
        total_avaliacoes_total=F('total_avaliacoes_colaborador') + F('total_avaliacoes_restaurante'),
        media_avaliacao_total=Case(
            When(total_avaliacoes_total=0, then=Value(0.0)),
            default=(
                (F('media_avaliacao_colaborador') * F('total_avaliacoes_colaborador') + 
                 F('media_avaliacao_restaurante') * F('total_avaliacoes_restaurante')) / 
                F('total_avaliacoes_total')
            ),
            output_field=FloatField()
        )
    ).order_by('id')
    
    cargo_selecionado = request.GET.get('cargo')
    hub_selecionado = request.GET.get('hub')
    search = request.GET.get('search', '')

    if cargo_selecionado:
        colaboradores = colaboradores.filter(cargo=cargo_selecionado)
    if hub_selecionado:
        colaboradores = colaboradores.filter(hub_id=hub_selecionado)
    if search:
        colaboradores = colaboradores.filter(nome__icontains=search)

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
            return redirect('home')
        else:
            return render(request, 'avaliacao/codigo_acesso.html', {'erro': 'Código incorreto.'})


def classificar_colaborador(media_geral):
    if media_geral is None:
        return "Sem avaliações suficientes"
    elif media_geral >= 4.8:
        return "Sujeito a promoção"
    elif media_geral >= 4.5:
        return "Sujeito a bonificação"
    elif media_geral >= 4.0:
        return "Sujeito a melhorias"
    elif media_geral >= 3.5:
        return "Sujeito a estagnação"
    elif media_geral >= 3.0:
        return "Sujeito a uma conversa de desempenho"
    else:
        return "Sujeito a demissão"



def perfil_colaborador(request, colaborador_id):
    if not request.user.is_superuser:
        return redirect('/admin/login/?next=' + request.path)
    
    colaborador = get_object_or_404(Colaborador, id=colaborador_id)
    template_to_render = 'avaliacao/perfil_colaborador.html' # Este é o único template agora

    # --- DADOS DO GESTOR (Lógica que já tínhamos) ---
    
    avaliacoes_gestor = None
    media_gestor = {}
    
    media_comportamental_labels = {
        'proatividade_media': 'Proatividade', 'responsabilidade_media': 'Responsabilidade',
        'trabalho_em_equipe_media': 'Trabalho em Equipe', 'comunicacao_media': 'Comunicação',
        'resiliencia_media': 'Resiliência', 'postura_profissional_media': 'Postura Profissional',
        'evolucao_individual_media': 'Evolução Individual',
    }
    media_operacional_mensageiro_labels = {
        'trm5_media': 'TRM5 (Agilidade)', 'erros_pedido_media': 'Erros de Pedido',
        'cumprimento_metas_media': 'Cumprimento de Metas', 'pontualidade_media': 'Pontualidade',
        'organizacao_praca_media': 'Organização da Praça', 'comunicacao_central_media': 'Com. com a Central',
    }
    media_operacional_assistente_labels = {
        'controle_fila_nba5_media': 'Controle Fila / NBA5', 'eficiencia_distribuicao_media': 'Eficiência Distribuição',
        'monitoramento_ativo_media': 'Monitoramento Ativo', 'cumprimento_processos_media': 'Cumpr. Processos',
        'resolucao_imprevistos_media': 'Resolução Imprevistos',
    }

    if colaborador.cargo == 'Mensageiro':
        avaliacoes_gestor = colaborador.avaliacaomensageiro_set.all().order_by('-data_avaliacao')
        media_agregada = avaliacoes_gestor.aggregate(
            **{key.replace('_media', ''): Avg(key.replace('_media', '')) for key in media_comportamental_labels.keys()},
            **{key.replace('_media', ''): Avg(key.replace('_media', '')) for key in media_operacional_mensageiro_labels.keys()}
        )
        media_gestor = {f"{key}_media": value for key, value in media_agregada.items()}

    elif colaborador.cargo == 'Assistente de Logística':
        avaliacoes_gestor = colaborador.avaliacaoassistente_set.all().order_by('-data_avaliacao')
        media_agregada = avaliacoes_gestor.aggregate(
            **{key.replace('_media', ''): Avg(key.replace('_media', '')) for key in media_comportamental_labels.keys()},
            **{key.replace('_media', ''): Avg(key.replace('_media', '')) for key in media_operacional_assistente_labels.keys()}
        )
        media_gestor = {f"{key}_media": value for key, value in media_agregada.items()}
    else:
        avaliacoes_gestor = AvaliacaoMensageiro.objects.none()
        media_gestor = {}

    # Cálculos gerais do GESTOR
    media_geral_gestor = avaliacoes_gestor.aggregate(media_geral=Avg('nota_final'))['media_geral']
    total_avaliacoes_gestor = avaliacoes_gestor.count()
    dois_meses_atras = datetime.now() - timedelta(days=60)
    avaliacoes_2m_gestor = avaliacoes_gestor.filter(data_avaliacao__gte=dois_meses_atras)
    media_mes_gestor = avaliacoes_2m_gestor.aggregate(media_geral=Avg('nota_final'))['media_geral']
    notas_evolucao_gestor = [a.nota_final for a in avaliacoes_gestor]
    medias_por_hub_gestor = avaliacoes_gestor.values('hub__nome').annotate(media_loja=Avg('nota_final'))
    
    # --- NOVO: DADOS DO RESTAURANTE (Lógica da view antiga) ---
    
    avaliacoes_restaurante = colaborador.avaliacoes_recebidas_restaurantes.all().order_by('-data_avaliacao')
    
    media_restaurante_labels = {
        'rapidez_atendimento_media': 'Rapidez Atendimento', 'eficiencia_resolucao_media': 'Eficiência Resolução',
        'clareza_comunicacao_media': 'Clareza Comunicação', 'profissionalismo_media': 'Profissionalismo',
        'suporte_gestao_pedidos_media': 'Suporte Pedidos', 'proatividade_media': 'Proatividade',
        'disponibilidade_media': 'Disponibilidade', 'satisfacao_geral_media': 'Satisfação Geral',
    }
    
    media_agregada_rest = avaliacoes_restaurante.aggregate(
        **{key.replace('_media', ''): Avg(key.replace('_media', '')) for key in media_restaurante_labels.keys()}
    )
    media_restaurante = {f"{key}_media": (value or 0) for key, value in media_agregada_rest.items()} # Garante 0 em vez de None

    # Cálculos gerais do RESTAURANTE
    media_geral_restaurante = avaliacoes_restaurante.aggregate(media_geral=Avg('nota_final'))['media_geral'] or 0
    total_avaliacoes_restaurante = avaliacoes_restaurante.count()
    notas_evolucao_restaurante = [a.nota_final for a in avaliacoes_restaurante]
    medias_por_restaurante = avaliacoes_restaurante.values('nome_restaurante').annotate(media_loja=Avg('nota_final'))

    # --- MÉDIA DOS 5 CRITÉRIOS MAIS IMPORTANTES ---
    top5_campos = []

    if colaborador.cargo == 'Mensageiro':
        top5_campos = [
            'cumprimento_metas',
            'responsabilidade',
            'comunicacao',
            'proatividade',
            'trm5',
        ]

    elif colaborador.cargo == 'Assistente de Logística':
        top5_campos = [
            'cumprimento_processos',
            'responsabilidade',
            'comunicacao',
            'proatividade',
            'controle_fila_nba5',
        ]

    # Calcula a média dos 5 melhores critérios
    media_top5 = None
    if avaliacoes_gestor.exists():
        media_top5 = avaliacoes_gestor.aggregate(
            media=Avg(
                sum(
                    F(campo) for campo in top5_campos
                ) / len(top5_campos)
            )
        )['media']

    classificacao = classificar_colaborador(media_top5) # Classificação baseada no gestor


    # --- CONTEXTO UNIFICADO ---
    
    context = {
        'colaborador': colaborador,
        'classificacao': classificacao,
        
        # Dados do Gestor
        'avaliacoes_gestor': avaliacoes_gestor,
        'media_gestor': media_gestor,
        'media_geral_gestor': media_geral_gestor,
        'total_avaliacoes_gestor': total_avaliacoes_gestor,
        'notas_evolucao_gestor': notas_evolucao_gestor,
        'medias_por_hub_gestor': medias_por_hub_gestor,
        'media_comportamental': media_comportamental_labels,
        'media_operacional_mensageiro': media_operacional_mensageiro_labels,
        'media_operacional_assistente': media_operacional_assistente_labels,
        
        # Dados do Restaurante
        'avaliacoes_restaurante': avaliacoes_restaurante,
        'media_restaurante': media_restaurante,
        'media_geral_restaurante': media_geral_restaurante,
        'total_avaliacoes_restaurante': total_avaliacoes_restaurante,
        'notas_evolucao_restaurante': notas_evolucao_restaurante,
        'medias_por_restaurante': medias_por_restaurante,
        'media_restaurante_labels': media_restaurante_labels,

        'media_top5': media_top5,
    }
    
    return render(request, template_to_render, context)



def avaliar_colaborador(request, colaborador_id):
    colaborador = get_object_or_404(Colaborador, id=colaborador_id)
    
    FormClass = None
    if colaborador.cargo == 'Mensageiro':
        FormClass = AvaliacaoMensageiroForm
    elif colaborador.cargo == 'Assistente de Logística':
        FormClass = AvaliacaoAssistenteForm
    
    if not FormClass:
        return render(request, 'erro.html', {'message': 'Não há formulário de avaliação para este cargo.'})

    if request.method == 'POST':
        form = FormClass(request.POST)
        if form.is_valid():
            avaliacao = form.save(commit=False)
            avaliacao.colaborador = colaborador
            if request.user.is_authenticated:
                avaliacao.avaliador = request.user
            if colaborador.hub:
                avaliacao.hub = colaborador.hub
                
            avaliacao.save()
            return render(request, 'avaliacao/avaliacao_enviada.html', {'colaborador': colaborador})
    else:
        form = FormClass()
    
    return render(request, 'avaliacao/avaliar_colaborador.html', {'form': form, 'colaborador': colaborador})


def avaliacao_restaurante(request, colaborador_id):
    colaborador = get_object_or_404(Colaborador, id=colaborador_id)
    
    if request.method == 'POST':
        form = AvaliacaoRestauranteForm(request.POST)
        if form.is_valid():
            avaliacao = form.save(commit=False)
            avaliacao.colaborador = colaborador
            if colaborador.hub:
                avaliacao.hub = colaborador.hub
            avaliacao.save()
            return render(request, 'avaliacao/avaliacao_enviada.html', {'colaborador': colaborador})
    else:
        form = AvaliacaoRestauranteForm()
    
    return render(request, 'avaliacao/avaliacao_restaurante.html', {'form': form, 'colaborador': colaborador})


def relatorio_op(request):
    if not request.user.is_superuser:
        return redirect('/admin/login/?next=' + request.path)
    return render(request, 'avaliacao/relatorio.html')


@csrf_exempt
@require_POST
def generate_report(request):
    try:
        data = json.loads(request.body)
        feedback = data.get('feedback', '')
        prompt = data.get('prompt', '')
        result = relatorio(feedback, prompt)
        return JsonResponse({'report': result})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def ranking(request):
    if not request.user.is_superuser:
        return redirect('/admin/login/?next=' + request.path)

    filtro = request.GET.get('filtro', 'media_geral')
    hub_id = request.GET.get('hub')

    colaboradores = Colaborador.objects.annotate(
        total_avaliacoes_mensageiro=Count('avaliacaomensageiro', distinct=True),
        total_avaliacoes_assistente=Count('avaliacaoassistente', distinct=True),
        # --- CORREÇÃO AQUI ---
        total_avaliacoes_restaurante=Count('avaliacoes_recebidas_restaurantes', distinct=True),
        media_mensageiro=Coalesce(Avg('avaliacaomensageiro__nota_final'), Value(0.0), output_field=FloatField()),
        media_assistente=Coalesce(Avg('avaliacaoassistente__nota_final'), Value(0.0), output_field=FloatField()),
        # --- CORREÇÃO AQUI ---
        media_avaliacao_restaurante=Coalesce(Avg('avaliacoes_recebidas_restaurantes__nota_final'), Value(0.0), output_field=FloatField()),
    ).annotate(
        total_avaliacoes_colaborador=F('total_avaliacoes_mensageiro') + F('total_avaliacoes_assistente'),
        media_avaliacao_colaborador=Case(
            When(total_avaliacoes_colaborador=0, then=Value(0.0)),
            default=(
                (F('media_mensageiro') * F('total_avaliacoes_mensageiro') + 
                 F('media_assistente') * F('total_avaliacoes_assistente')) / 
                F('total_avaliacoes_colaborador')
            ),
            output_field=FloatField()
        ),
    ).annotate(
        total_avaliacoes=F('total_avaliacoes_colaborador') + F('total_avaliacoes_restaurante'),
        media_geral=Case(
            When(total_avaliacoes=0, then=Value(0.0)),
            default=(
                (F('media_avaliacao_colaborador') * F('total_avaliacoes_colaborador') + 
                 F('media_avaliacao_restaurante') * F('total_avaliacoes_restaurante')) / 
                F('total_avaliacoes')
            ),
            output_field=FloatField()
        ),
        qtd_medalhas=Count('medalhas', distinct=True),
    )
    
    # Lógica de filtros complexos (exemplo)
    if filtro == 'pontualidade':
        colaboradores = colaboradores.filter(cargo='Mensageiro').annotate(
            media_pontualidade=Avg('avaliacaomensageiro__pontualidade')
        )
    elif filtro == 'resolucao_imprevistos':
         colaboradores = colaboradores.filter(cargo='Assistente de Logística').annotate(
            media_resolucao_imprevistos=Avg('avaliacaoassistente__resolucao_imprevistos')
        )
    elif filtro == 'proatividade':
        colaboradores = colaboradores.annotate(
            media_proat_mensageiro=Coalesce(Avg('avaliacaomensageiro__proatividade'), Value(0.0)),
            media_proat_assistente=Coalesce(Avg('avaliacaoassistente__proatividade'), Value(0.0))
        ).annotate(
            media_proatividade=Case(
                When(total_avaliacoes_colaborador=0, then=Value(0.0)),
                default=(
                    (F('media_proat_mensageiro') * F('total_avaliacoes_mensageiro') +
                     F('media_proat_assistente') * F('total_avaliacoes_assistente')) /
                    F('total_avaliacoes_colaborador')
                ),
                output_field=FloatField()
            )
        )
    # (Adicione aqui a lógica para os outros filtros comportamentais e operacionais)

    if hub_id:
        colaboradores = colaboradores.filter(hub_id=hub_id)

    filtros_ordenacao = {
        'media_geral': '-media_geral',
        'pontualidade': '-media_pontualidade',
        'resolucao_imprevistos': '-media_resolucao_imprevistos',
        'proatividade': '-media_proatividade',
        # (Adicione os outros campos)
    }
    
    ordem = filtros_ordenacao.get(filtro, '-media_geral')
    colaboradores = colaboradores.order_by(ordem)

    titulos_filtro = {
        'media_geral': 'Ranking Geral',
        'pontualidade': 'Mais Pontuais (Mensageiros)',
        'proatividade': 'Mais Proativos (Geral)',
        'resolucao_imprevistos': 'Resolução de Imprevistos (Assistentes)',
        # (Adicione os outros)
    }
    
    filtros_disponiveis = [
        ('media_geral', 'Ranking Geral'),
        ('proatividade', 'Proatividade'),
        ('pontualidade', 'Pontualidade (Mensageiros)'),
        ('resolucao_imprevistos', 'Res. Imprevistos (Assistentes)'),
        # (Adicione os outros)
    ]

    context = {
        'colaboradores': colaboradores,
        'filtro_atual': filtro,
        'titulo_ranking': titulos_filtro.get(filtro, 'Ranking Geral'),
        'filtros_disponiveis': filtros_disponiveis,
        'hubs': Hub.objects.all(),
        'hub_selecionado': hub_id,
    }

    return render(request, 'avaliacao/ranking.html', context)



def gerar_sugestoes_medalhas():
    colaboradores = Colaborador.objects.all()

    for colab in colaboradores:

        # =======================
        # TEMPO DE EMPRESA
        # =======================
        if colab.data_contratacao:
            anos = (timezone.now().date().year - colab.data_contratacao.year)

            if anos == 1:
                SugestaoMedalha.objects.get_or_create(
                    colaborador=colab,
                    tipo="1_ano",
                    status="pendente",
                )

            elif anos == 2:
                SugestaoMedalha.objects.get_or_create(
                    colaborador=colab,
                    tipo="2_anos",
                    status="pendente",
                )

            elif anos == 3:
                SugestaoMedalha.objects.get_or_create(
                    colaborador=colab,
                    tipo="3_anos",
                    status="pendente",
                )

        # =======================
        # NOTAS – ULTIMAS AVALIAÇÕES
        # =======================
        aval = (
            AvaliacaoMensageiro.objects.filter(colaborador=colab).order_by('-data_avaliacao').first() or
            AvaliacaoAssistente.objects.filter(colaborador=colab).order_by('-data_avaliacao').first()
        )

        if not aval:
            continue

        nota_final = aval.nota_final or 0
        comportamento = aval.nota_comportamental or 0
        operacional = aval.nota_operacional or 0

        # Destaque geral
        if nota_final >= 4.7:
            SugestaoMedalha.objects.get_or_create(
                colaborador=colab,
                tipo="destaque",
                status="pendente"
            )

        # Comunicação
        if aval.comunicacao >= 4.2:
            SugestaoMedalha.objects.get_or_create(
                colaborador=colab,
                tipo="comunicação",
                status="pendente"
            )

        # Carisma → postura
        if aval.postura_profissional >= 4.5:
            SugestaoMedalha.objects.get_or_create(
                colaborador=colab,
                tipo="carisma",
                status="pendente"
            )

        # Dedicação
        if aval.proatividade >= 4.5:
            SugestaoMedalha.objects.get_or_create(
                colaborador=colab,
                tipo="dedicação",
                status="pendente"
            )

        # Super Pontual
        if hasattr(aval, "pontualidade") and aval.pontualidade >= 4.5:
            SugestaoMedalha.objects.get_or_create(
                colaborador=colab,
                tipo="pontual",
                status="pendente"
            )

        # Logística Implacável
        if operacional >= 4.5:
            SugestaoMedalha.objects.get_or_create(
                colaborador=colab,
                tipo="logistica",
                status="pendente"
            )


def painel_medalhas(request):
    if not request.user.is_superuser:
        return redirect('/admin/login/?next=' + request.path)
    sugestoes = SugestaoMedalha.objects.order_by('-criado_em')
    return render(request, "avaliacao/painel_medalhas.html", {"sugestoes": sugestoes})


def aceitar_sugestao(request, sugestao_id):
    sugestao = get_object_or_404(SugestaoMedalha, id=sugestao_id)

    # Criar medalha definitiva
    Medalha.objects.create(
        colaborador=sugestao.colaborador,
        tipo=sugestao.tipo,
        descricao=sugestao.motivo
    )

    # Remove da lista de sugestões
    sugestao.delete()

    return redirect("painel_medalhas")


def excluir_sugestao(request, sugestao_id):
    sugestao = get_object_or_404(SugestaoMedalha, id=sugestao_id)
    sugestao.delete()
    return redirect("painel_medalhas")

