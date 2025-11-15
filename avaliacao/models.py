from django.utils import timezone
from django.db import models
from django.core.files.base import ContentFile
from PIL import Image as PilImage
import io
from datetime import date



class Hub(models.Model):
    nome = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.nome
    

class Colaborador(models.Model):
    CARGO_CHOICES = [
        ('Líder de Logística', 'Líder de Logística'),
        ('Assistente de Logística', 'Assistente de Logística'),
        ('Mensageiro', 'Mensageiro'),
        ('Supervisor', 'Supervisor'),
        ('Staff', 'Staff'),
    ]

    nome = models.CharField(max_length=100)
    cargo = models.CharField(max_length=100, choices=CARGO_CHOICES, null=True)  # Permitir nulo
    data_contratacao = models.DateField(null=True, blank=True)  # Permitir nulo e vazio
    imagem = models.ImageField(upload_to='media/')
    hub = models.ForeignKey(Hub, on_delete=models.SET_NULL, null=True, blank=True)

    def total_medalhas(self):
        return sum(medalha.quantidade for medalha in self.medalhas.all())  # Soma as medalhas do colaborador

    @property
    def tempo_na_empresa(self):
        if not self.data_contratacao:
            return "Data de contratação não definida"
        
        try:
            hoje = date.today()
            anos = hoje.year - self.data_contratacao.year
            meses = hoje.month - self.data_contratacao.month
            
            # Ajuste se o mês atual é anterior ao mês de contratação
            if meses < 0:
                anos -= 1
                meses += 12
            
            # Formatar a string de tempo
            partes_tempo = []
            if anos > 0:
                partes_tempo.append(f"{anos} anos")
            if meses > 0:
                partes_tempo.append(f"{meses} meses")
            
            return ", ".join(partes_tempo) if partes_tempo else "Menos de 1 mês"
        
        except Exception as e:
            return f"Erro ao calcular o tempo na empresa: {e}"


    def save(self, *args, **kwargs):
        # Redimensionar a imagem
        if self.imagem:
            img = PilImage.open(self.imagem)
            img = img.convert('RGB')  # Converter para RGB se a imagem for PNG ou com canal alfa

            # Dimensões desejadas
            target_size = (816, 816)

            # Redimensiona e faz o corte central para garantir o tamanho exato
            img.thumbnail(target_size, PilImage.LANCZOS)
            left = (img.width - target_size[0]) / 2
            top = (img.height - target_size[1]) / 2
            right = (img.width + target_size[0]) / 2
            bottom = (img.height + target_size[1]) / 2
            img = img.crop((left, top, right, bottom))

            # Salvar a imagem redimensionada em um buffer
            img_io = io.BytesIO()
            img.save(img_io, format='JPEG', quality=85)  # Salvar como JPEG
            img_file = ContentFile(img_io.getvalue(), name=self.imagem.name)
            self.imagem = img_file

        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome  # Retorna o nome do colaborador

    class Meta:
        verbose_name = "Colaborador"
        verbose_name_plural = "Colaboradores"


class Medalha(models.Model):
    TIPOS_MEDALHA = [
        ("1_ano", "1 Ano de Hub"),
        ("2_anos", "2 Anos de Hub"),
        ("3_anos", "3 Anos de Hub"),
        ("logistica", "Logística Implacável"),
        ("mensageiro", "1# Mensageiro"),
        ("pontual", "Super Pontual"),
        ("criatividade", "Criatividade"),
        ("destaque", "Colaborador Destaque"),
        ("comunicação", "Comunicação Eficiente"),
        ("carisma", "Carisma"),
        ("dedicação", "Dedicação"),
        ("analista", "Analista de Dados"),

    ]

    colaborador = models.ForeignKey("Colaborador", related_name="medalhas", on_delete=models.CASCADE)
    tipo = models.CharField(max_length=50, choices=TIPOS_MEDALHA, blank=True, null=True)  # Tipo fixo
    descricao = models.TextField(blank=True, null=True)  # Descrição opcional

    def get_medalha_url(self):
        """Retorna a URL da imagem correspondente ao tipo de medalha"""
        return f"/static/medalhas/{self.tipo}.png" if self.tipo else None

    def __str__(self):
        return f"{self.colaborador.nome} - {self.get_tipo_display()}"

    class Meta:
        verbose_name = "Medalha"
        verbose_name_plural = "Medalhas"


class SugestaoMedalha(models.Model):
    colaborador = models.ForeignKey(Colaborador, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=50, choices=Medalha.TIPOS_MEDALHA)
    motivo = models.TextField(blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sugestão: {self.colaborador.nome} - {self.get_tipo_display()}"


# Constante para as notas (1-5)
NOTAS_CHOICES = [
    (1, '1 - Muito Abaixo'),
    (2, '2 - Abaixo do Esperado'),
    (3, '3 - Esperado'),
    (4, '4 - Acima do Esperado'),
    (5, '5 - Excepcional'),
]

class AvaliacaoBase(models.Model):
    """ 
    MODELO ABSTRATO: Contém os campos comuns a todas as avaliações de GESTOR.
    (Info Básica + Parâmetros Comportamentais)
    """
    
    # --- Informações Básicas ---
    # avaliador = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="avaliacoes_feitas", verbose_name="Gestor Avaliador")
    avaliador = models.CharField(max_length=255)
    hub = models.ForeignKey(Hub, on_delete=models.SET_NULL, null=True, verbose_name="Hub da Avaliação")
    colaborador = models.ForeignKey(Colaborador, on_delete=models.CASCADE, verbose_name="Colaborador Avaliado")
    data_avaliacao = models.DateField(default=timezone.now, verbose_name="Data da Avaliação")

    # --- 🧠 PARÂMETROS COMPORTAMENTAIS (Comuns a todos) ---
    proatividade = models.PositiveSmallIntegerField(choices=NOTAS_CHOICES)
    responsabilidade = models.PositiveSmallIntegerField(choices=NOTAS_CHOICES)
    trabalho_em_equipe = models.PositiveSmallIntegerField(choices=NOTAS_CHOICES, verbose_name="Trabalho em Equipe")
    comunicacao = models.PositiveSmallIntegerField(choices=NOTAS_CHOICES, verbose_name="Comunicação Comportamental")
    resiliencia = models.PositiveSmallIntegerField(choices=NOTAS_CHOICES)
    postura_profissional = models.PositiveSmallIntegerField(choices=NOTAS_CHOICES, verbose_name="Postura Profissional")
    evolucao_individual = models.PositiveSmallIntegerField(choices=NOTAS_CHOICES, verbose_name="Evolução Individual")

    # --- Comentários ---
    comentario_comportamental = models.TextField(null=True, blank=True, verbose_name="Observações Comportamentais")
    comentario_operacional = models.TextField(null=True, blank=True, verbose_name="Observações Operacionais")

    # --- Notas Finais (Calculadas) ---
    nota_comportamental = models.FloatField(null=True, blank=True, verbose_name="Média Comportamental")
    nota_operacional = models.FloatField(null=True, blank=True, verbose_name="Média Operacional")
    nota_final = models.FloatField(null=True, blank=True, verbose_name="Nota Final")
    
    class Meta:
        abstract = True # Não cria uma tabela no BD, serve apenas de base
        ordering = ['-data_avaliacao', 'colaborador']

    def calcular_media_comportamental(self):
        """ Calcula a média das notas comportamentais """
        notas = [
            self.proatividade, self.responsabilidade, self.trabalho_em_equipe,
            self.comunicacao, self.resiliencia, self.postura_profissional,
            self.evolucao_individual
        ]
        # Filtra notas None (caso alguma seja opcional no futuro)
        notas_validas = [n for n in notas if n is not None]
        if notas_validas:
            self.nota_comportamental = sum(notas_validas) / len(notas_validas)
        else:
            self.nota_comportamental = None

    def calcular_media_final(self):
        """ Calcula a média final (50/50 entre operacional e comportamental) """
        if self.nota_comportamental is not None and self.nota_operacional is not None:
            self.nota_final = (self.nota_comportamental + self.nota_operacional) / 2
        elif self.nota_comportamental is not None:
            self.nota_final = self.nota_comportamental
        elif self.nota_operacional is not None:
            self.nota_final = self.nota_operacional
        else:
            self.nota_final = None

    def __str__(self):
        # self.__class__.__name__ pega o nome da classe filha (ex: "AvaliacaoMensageiro")
        return f"{self.__class__.__name__} de {self.colaborador.nome} em {self.data_avaliacao}"


class AvaliacaoMensageiro(AvaliacaoBase):
    """ 
    Avaliação do GESTOR para o MENSAGEIRO.
    Herda os campos comportamentais e adiciona os operacionais.
    """
    
    # --- 🧩 PARÂMETROS OPERACIONAIS (Mensageiro) ---
    trm5 = models.PositiveSmallIntegerField(choices=NOTAS_CHOICES, verbose_name="TRM5 (Agilidade Carrossel)")
    erros_pedido = models.PositiveSmallIntegerField(choices=NOTAS_CHOICES, verbose_name="Erros de Pedido")
    cumprimento_metas = models.PositiveSmallIntegerField(choices=NOTAS_CHOICES, verbose_name="Cumprimento de Metas Diárias")
    pontualidade = models.PositiveSmallIntegerField(choices=NOTAS_CHOICES)
    organizacao_praca = models.PositiveSmallIntegerField(choices=NOTAS_CHOICES, verbose_name="Organização da Praça")
    comunicacao_central = models.PositiveSmallIntegerField(choices=NOTAS_CHOICES, verbose_name="Comunicação com a Central")

    def save(self, *args, **kwargs):
        # 1. Calcula média comportamental (método do pai)
        self.calcular_media_comportamental()
        
        # 2. Calcula média operacional (específica deste modelo)
        notas_op = [
            self.trm5, self.erros_pedido, self.cumprimento_metas,
            self.pontualidade, self.organizacao_praca, self.comunicacao_central
        ]
        notas_op_validas = [n for n in notas_op if n is not None]
        if notas_op_validas:
            self.nota_operacional = sum(notas_op_validas) / len(notas_op_validas)
        else:
            self.nota_operacional = None
            
        # 3. Calcula média final (método do pai)
        self.calcular_media_final()
        
        super().save(*args, **kwargs)
        
    class Meta:
        verbose_name = "Avaliação de Mensageiro"
        verbose_name_plural = "Avaliações de Mensageiros"


class AvaliacaoAssistente(AvaliacaoBase):
    """ 
    Avaliação do GESTOR para o ASSISTENTE DE LOGÍSTICA.
    Herda os campos comportamentais e adiciona os operacionais.
    """
    
    # --- 🧩 PARÂMETROS OPERACIONAIS (Assistente) ---
    controle_fila_nba5 = models.PositiveSmallIntegerField(choices=NOTAS_CHOICES, verbose_name="Controle de Fila / NBA5")
    eficiencia_distribuicao = models.PositiveSmallIntegerField(choices=NOTAS_CHOICES, verbose_name="Eficiência na Distribuição")
    monitoramento_ativo = models.PositiveSmallIntegerField(choices=NOTAS_CHOICES, verbose_name="Monitoramento Ativo da Praça")
    cumprimento_processos = models.PositiveSmallIntegerField(choices=NOTAS_CHOICES, verbose_name="Cumprimento de Processos Padrão")
    resolucao_imprevistos = models.PositiveSmallIntegerField(choices=NOTAS_CHOICES, verbose_name="Resolução de Imprevistos")

    def save(self, *args, **kwargs):
        # 1. Calcula média comportamental (método do pai)
        self.calcular_media_comportamental()
        
        # 2. Calcula média operacional (específica deste modelo)
        notas_op = [
            self.controle_fila_nba5, self.eficiencia_distribuicao, self.monitoramento_ativo,
            self.cumprimento_processos, self.resolucao_imprevistos
        ]
        notas_op_validas = [n for n in notas_op if n is not None]
        if notas_op_validas:
            self.nota_operacional = sum(notas_op_validas) / len(notas_op_validas)
        else:
            self.nota_operacional = None
            
        # 3. Calcula média final (método do pai)
        self.calcular_media_final()
        
        super().save(*args, **kwargs)
        
    class Meta:
        verbose_name = "Avaliação de Assistente"
        verbose_name_plural = "Avaliações de Assistentes"

# NOTA: Se 'Líder de Logística', 'Supervisor' ou 'Staf' tiverem
# métricas operacionais *diferentes*, você pode criar novas classes
# (ex: AvaliacaoLider) que também herdam de AvaliacaoBase.


# ---
# 4. Modelo de Avaliação (Restaurante)
# ---

class AvaliacaoRestaurante(models.Model):
    """ 
    Avaliação feita PELO RESTAURANTE sobre o colaborador do Hub.
    Este é um modelo separado e não herda do AvaliacaoBase.
    (Baseado nos campos do seu modelo antigo, que faziam sentido)
    """
    
    # --- Informações Básicas ---
    nome_restaurante = models.CharField(max_length=255, verbose_name="Nome do Restaurante")
    nome_avaliador_restaurante = models.CharField(max_length=255, verbose_name="Nome do Avaliador (Restaurante)", blank=True)
    
    hub = models.ForeignKey(Hub, on_delete=models.SET_NULL, null=True, related_name="avaliacoes_de_restaurantes")
    # related_name diferente para não dar conflito com as avaliações do gestor
    colaborador = models.ForeignKey(Colaborador, on_delete=models.CASCADE, related_name="avaliacoes_recebidas_restaurantes")
    data_avaliacao = models.DateField(default=timezone.now, verbose_name="Data da Avaliação")

    # --- Critérios (reutilizei os do seu primeiro post) ---
    rapidez_atendimento = models.PositiveSmallIntegerField(choices=NOTAS_CHOICES)
    eficiencia_resolucao = models.PositiveSmallIntegerField(choices=NOTAS_CHOICES)
    clareza_comunicacao = models.PositiveSmallIntegerField(choices=NOTAS_CHOICES)
    profissionalismo = models.PositiveSmallIntegerField(choices=NOTAS_CHOICES)
    suporte_gestao_pedidos = models.PositiveSmallIntegerField(choices=NOTAS_CHOICES)
    proatividade = models.PositiveSmallIntegerField(choices=NOTAS_CHOICES)
    disponibilidade = models.PositiveSmallIntegerField(choices=NOTAS_CHOICES)
    satisfacao_geral = models.PositiveSmallIntegerField(choices=NOTAS_CHOICES)

    comentario = models.TextField(null=True, blank=True)
    nota_final = models.FloatField(null=True, blank=True)

    def save(self, *args, **kwargs):
        notas = [
            self.rapidez_atendimento, self.eficiencia_resolucao, self.clareza_comunicacao,
            self.profissionalismo, self.suporte_gestao_pedidos, self.proatividade,
            self.disponibilidade, self.satisfacao_geral
        ]
        notas_validas = [n for n in notas if n is not None]
        if notas_validas:
            self.nota_final = sum(notas_validas) / len(notas_validas)
        else:
            self.nota_final = None
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Aval. Restaurante ({self.nome_restaurante}) para {self.colaborador.nome}"
    
    class Meta:
        verbose_name = "Avaliação do Restaurante"
        verbose_name_plural = "Avaliações dos Restaurantes"
        ordering = ['-data_avaliacao']
