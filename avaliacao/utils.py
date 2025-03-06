from langchain_community.document_loaders import WebBaseLoader
from langchain.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
import os

def analizar_partida(dados_avaliacao):
    feedback = f"Feedback para {dados_avaliacao['nome']}:\n"
    # Avaliações individuais (Nota máxima 5)
    feedback += f"Pontualidade: {dados_avaliacao['pontualidade']}/5\n"
    feedback += f"Organização: {dados_avaliacao['organizacao']}/5\n"
    feedback += f"Comunicação: {dados_avaliacao['comunicacao']}/5\n"
    feedback += f"Resolução de Problemas: {dados_avaliacao['resolucao_problemas']}/5\n"
    feedback += f"Precisão: {dados_avaliacao['precisao']}/5\n"
    feedback += f"Velocidade: {dados_avaliacao['velocidade']}/5\n"
    feedback += f"Conhecimento de Ferramentas: {dados_avaliacao['conhecimento_ferramentas']}/5\n"
    feedback += f"Flexibilidade: {dados_avaliacao['flexibilidade']}/5\n"
    feedback += f"Postura Profissional: {dados_avaliacao['postura_profissional']}/5\n"
    feedback += f"Priorização de Tarefas: {dados_avaliacao['priorizacao_tarefas']}/5\n"
    feedback += f"Pontualidade: {dados_avaliacao['comentario']}/5\n"

    
    # Calculando a nota média (com base em 5)
    # nota_media = sum([dados_avaliacao[key] for key in dados_avaliacao if key != 'nome' and key != 'comentarios']) / 
    nota_media = sum([dados_avaliacao[key] for key in dados_avaliacao if key != 'nome' and key != 'comentarios' and isinstance(dados_avaliacao[key], (int, float))]) / 10

    feedback += f"\nNota Média: {nota_media:.2f}/5\n"

    # Concatena conteúdo dos documentos
    documento = feedback
    # for doc in feedback:
    #     documento = documento + doc.page_content

    api_key = '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'

    os.environ['GROQ_API_KEY'] = api_key

    # Inicializa o ChatGroq
    chat = ChatGroq(model='llama-3.3-70b-versatile')

    template = ChatPromptTemplate.from_messages([
        ('system', 'Você será um analista de colaboradores e, com base nos dados fornecidos, irá fornecer feedback direto e objetivo sobre o colaborador. Seu feedback deve ser assertivo e focado nas ações e comportamentos descritos, evitando listas, tópicos ou formatação de quebra. Seja específico e claro, buscando sempre uma abordagem construtiva e prática. Os dados fornecidos são: {documentos_informados}.'),
        ('user', '{input}')
    ])


    chain = template | chat
    resposta = chain.invoke({'documentos_informados': documento, 'input': "Forneça uma análise objetiva e prática sobre o colaborador, com base nos dados fornecidos, para que o gestor possa dar um feedback claro e construtivo. Destaque pontos fortes, áreas para desenvolvimento e recomendações diretas que o gestor possa comunicar ao colaborador de forma eficaz."})

    return resposta.content



def gerar_feedback_restaurante(dados_avaliacao):
    feedback = f"Feedback para {dados_avaliacao['nome']}:\n"
    feedback += f"Rapidez no Atendimento: {dados_avaliacao['rapidez_atendimento']}/5\n"
    feedback += f"Eficiência na Resolução: {dados_avaliacao['eficiencia_resolucao']}/5\n"
    feedback += f"Clareza na Comunicação: {dados_avaliacao['clareza_comunicacao']}/5\n"
    feedback += f"Profissionalismo: {dados_avaliacao['profissionalismo']}/5\n"
    feedback += f"Suporte na Gestão de Pedidos: {dados_avaliacao['suporte_gestao_pedidos']}/5\n"
    feedback += f"Proatividade: {dados_avaliacao['proatividade']}/5\n"
    feedback += f"Disponibilidade: {dados_avaliacao['disponibilidade']}/5\n"
    feedback += f"Satisfação Geral: {dados_avaliacao['satisfacao_geral']}/5\n"

    nota_media = sum([dados_avaliacao[key] for key in dados_avaliacao if key not in ['nome', 'comentario']]) / 8
    feedback += f"\nNota Média: {nota_media:.2f}/5\n"

    documento = feedback
    # for doc in feedback:
    #     documento = documento + doc.page_content

    api_key = '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'

    os.environ['GROQ_API_KEY'] = api_key

    # Inicializa o ChatGroq
    chat = ChatGroq(model='llama-3.3-70b-versatile')

    template = ChatPromptTemplate.from_messages([
        ('system', 'Você será um analista de colaboradores e, com base nos dados fornecidos, irá fornecer feedback direto e objetivo sobre o colaborador. Seu feedback deve ser assertivo e focado nas ações e comportamentos descritos, evitando listas, tópicos ou formatação de quebra. Seja específico e claro, buscando sempre uma abordagem construtiva e prática. Os dados fornecidos são: {documentos_informados}.'),
        ('user', '{input}')
    ])


    chain = template | chat
    resposta = chain.invoke({'documentos_informados': documento, 'input': "Forneça uma análise objetiva e prática sobre o colaborador, com base nos dados fornecidos, para que o gestor possa dar um feedback claro e construtivo. Destaque pontos fortes, áreas para desenvolvimento e recomendações diretas que o gestor possa comunicar ao colaborador de forma eficaz."})

    return resposta.content