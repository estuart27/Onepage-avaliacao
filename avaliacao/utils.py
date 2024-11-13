import os
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate

# Função única para gerar e processar o feedback
def resposta_bot(dados_avaliacao):
    """
    Gera o feedback para o colaborador com base nos dados de avaliação.
    A nota máxima é ajustada para 5 e o feedback é refinado pela IA.
    """
    # Gera o feedback inicial com base nas avaliações
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
    
    # Calculando a nota média (com base em 5)
    nota_media = sum([dados_avaliacao[key] for key in dados_avaliacao if key != 'nome']) / 10
    feedback += f"\nNota Média: {nota_media:.2f}/5\n"
    
    # Configuração da chave da API para a IA (ChatGroq)
    api_key = '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'
    os.environ['GROQ_API_KEY'] = api_key
    
    # Criação do objeto de modelo de chat
    chat = ChatGroq(model='llama-3.1-70b-versatile')
    
    # Ajustando as mensagens para não usar 'role'
    mensagens_modelo = [
        f"Você é um assistente que fornece feedback detalhado para colaboradores com base nas suas avaliações.",
        f"Aqui está o feedback gerado: {feedback}"
    ]
    
    # Gera o feedback final usando o modelo
    resposta_ia = chat.generate(messages=mensagens_modelo)  # Usando o método generate corretamente
    
    # Retorna o feedback gerado
    return resposta_ia['text']
