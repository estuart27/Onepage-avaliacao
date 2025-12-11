import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from django.conf import settings
from .models import Colaborador, AvaliacaoMensageiro, AvaliacaoAssistente, AvaliacaoRestaurante

def formatar_dados_historicos(colaborador):
    """
    Coleta as últimas 6 avaliações de gestor e restaurante para criar uma linha do tempo.
    """
    historico_texto = f"DADOS DO COLABORADOR: {colaborador.nome} | Cargo: {colaborador.cargo} | Tempo de Casa: {colaborador.tempo_na_empresa}\n"
    historico_texto += "=" * 50 + "\n\n"

    # 1. Buscar avaliações de Gestor (Verifica qual o tipo de avaliação baseada no cargo ou busca em ambas)
    # Trazemos as últimas 6 para análise de tendência
    avs_mensageiro = AvaliacaoMensageiro.objects.filter(colaborador=colaborador).order_by('-data_avaliacao')[:6]
    avs_assistente = AvaliacaoAssistente.objects.filter(colaborador=colaborador).order_by('-data_avaliacao')[:6]
    
    # Junta as listas e reordena por data (caso o colaborador tenha mudado de cargo)
    todas_avs_gestor = sorted(list(avs_mensageiro) + list(avs_assistente), key=lambda x: x.data_avaliacao, reverse=True)

    if not todas_avs_gestor:
        historico_texto += "Nenhuma avaliação de gestor encontrada.\n"
    
    for av in todas_avs_gestor:
        tipo = "Mensageiro" if isinstance(av, AvaliacaoMensageiro) else "Assistente"
        historico_texto += f"--- AVALIAÇÃO GESTOR ({av.data_avaliacao.strftime('%d/%m/%Y')}) ---\n"
        historico_texto += f"Tipo: {tipo} | Nota Final: {av.nota_final:.2f} (Comportamental: {av.nota_comportamental:.2f} | Operacional: {av.nota_operacional:.2f})\n"
        
        # Detalhes Críticos
        historico_texto += f"Pontos: Proatividade {av.proatividade}, Responsabilidade {av.responsabilidade}, Trabalho em Equipe {av.trabalho_em_equipe}\n"
        
        # Adicionar métricas operacionais específicas se existirem
        if tipo == "Mensageiro":
            historico_texto += f"Operacional: TRM5 {av.trm5}, Erros {av.erros_pedido}, Metas {av.cumprimento_metas}\n"
        elif tipo == "Assistente":
            historico_texto += f"Operacional: Fila/NBA5 {av.controle_fila_nba5}, Eficiência {av.eficiencia_distribuicao}\n"

        if av.comentario_comportamental:
            historico_texto += f"Obs. Comportamental: {av.comentario_comportamental}\n"
        if av.comentario_operacional:
            historico_texto += f"Obs. Operacional: {av.comentario_operacional}\n"
        historico_texto += "\n"

    # 2. Buscar avaliações de Restaurantes (Visão Externa)
    avs_restaurante = AvaliacaoRestaurante.objects.filter(colaborador=colaborador).order_by('-data_avaliacao')[:6]
    
    if avs_restaurante:
        historico_texto += "-" * 50 + "\nFEEDBACK DOS RESTAURANTES (Visão Externa):\n"
        for av in avs_restaurante:
            historico_texto += f"Data: {av.data_avaliacao.strftime('%d/%m/%Y')} | Restaurante: {av.nome_restaurante} | Nota: {av.nota_final:.2f}\n"
            historico_texto += f"Avaliação: Rapidez {av.rapidez_atendimento}, Profissionalismo {av.profissionalismo}\n"
            if av.comentario:
                historico_texto += f"Comentário: {av.comentario}\n"
            historico_texto += "\n"

    return historico_texto

def gerar_analise_ia_colaborador(colaborador_id):
    try:
        colaborador = Colaborador.objects.get(id=colaborador_id)
    except Colaborador.DoesNotExist:
        return "Colaborador não encontrado."

    # Prepara os dados
    dados_contexto = formatar_dados_historicos(colaborador)

    # Configuração da API (Idealmente, use settings.py para a chave)

    api_key = os.getenv("GROQ_API_KEY")    
    os.environ['GROQ_API_KEY'] = api_key 

    chat = ChatGroq(model='llama-3.3-70b-versatile', temperature=0.3) # Temperature baixa para ser mais analítico e menos criativo

    template = ChatPromptTemplate.from_messages([
        ('system', """
         Você é um Consultor de RH Sênior especializado em Logística e Performance. 
         Sua tarefa é analisar o histórico de avaliações de um colaborador e gerar um relatório de feedback para o gestor.
         
         Instruções:
         1. **Análise de Tendência**: O colaborador está evoluindo, estagnado ou regredindo nas notas mês a mês?
         2. **Cruzamento de Dados**: Compare a visão do GESTOR (Interna) com a do RESTAURANTE (Externa). Existe discrepância? (Ex: Gestor acha ótimo, mas restaurante reclama da demora).
         3. **Pontos Fortes e Fracos**: Identifique padrões recorrentes nos dados numéricos e comentários.
         4. **Plano de Ação**: Sugira 3 ações práticas para o gestor aplicar com esse colaborador no próximo ciclo.

         Formatação de Saída (Use Markdown):
         - Use emojis moderados para leitura agradável.
         - Seja direto. Não encha linguiça.
         - Foco total em melhoria de performance.
         """),
        ('user', 'Analise os seguintes dados históricos deste colaborador e me dê o resumo executivo:\n\n{dados_historicos}')
    ])

    chain = template | chat
    resposta = chain.invoke({'dados_historicos': dados_contexto})

    return resposta.content