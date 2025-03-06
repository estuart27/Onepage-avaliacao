# avaliacao/models.py
from django.db import models
from django.db import models
from django.core.files.base import ContentFile
from PIL import Image as PilImage
import io
from datetime import date, timedelta


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
        ('Staf', 'Staf'),
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


class Avaliacao(models.Model):
    # Campos de avaliação
    avaliador = models.CharField(max_length=255)
    loja = models.CharField(max_length=255)
    colaborador = models.ForeignKey(Colaborador, on_delete=models.CASCADE, related_name="avaliacoes")
    pontualidade = models.IntegerField()
    organizacao = models.IntegerField()
    comunicacao = models.IntegerField()
    resolucao_problemas = models.IntegerField()
    precisao = models.IntegerField()
    velocidade = models.IntegerField()
    conhecimento_ferramentas = models.IntegerField()
    flexibilidade = models.IntegerField()
    postura_profissional = models.IntegerField()
    priorizacao_tarefas = models.IntegerField()
    comentario = models.TextField(null=True, blank=True)
    data = models.DateField(auto_now_add=True)

    # Campo `nota` para armazenar a média das avaliações
    nota = models.FloatField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Substituindo campos None por 0
        self.pontualidade = self.pontualidade or 0
        self.organizacao = self.organizacao or 0
        self.comunicacao = self.comunicacao or 0
        self.resolucao_problemas = self.resolucao_problemas or 0
        self.precisao = self.precisao or 0
        self.velocidade = self.velocidade or 0
        self.conhecimento_ferramentas = self.conhecimento_ferramentas or 0
        self.flexibilidade = self.flexibilidade or 0
        self.postura_profissional = self.postura_profissional or 0
        self.priorizacao_tarefas = self.priorizacao_tarefas or 0

        # Calcula a média das avaliações e armazena em `nota`
        self.nota = (
            self.pontualidade + self.organizacao + self.comunicacao +
            self.resolucao_problemas + self.precisao + self.velocidade +
            self.conhecimento_ferramentas + self.flexibilidade +
            self.postura_profissional + self.priorizacao_tarefas
        ) / 10

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Avaliação de {self.colaborador} em {self.data}"


from django.db import models

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



class Avaliacao_Restaurante(models.Model):
    # Informações do avaliador e do colaborador avaliado
    avaliador = models.CharField(max_length=255)
    loja = models.CharField(max_length=255)
    colaborador = models.ForeignKey(Colaborador, on_delete=models.CASCADE, related_name="avaliacoes_restaurantes")

    # Critérios de avaliação (notas de 1 a 5)
    rapidez_atendimento = models.IntegerField()
    eficiencia_resolucao = models.IntegerField()
    clareza_comunicacao = models.IntegerField()
    profissionalismo = models.IntegerField()
    suporte_gestao_pedidos = models.IntegerField()
    proatividade = models.IntegerField()
    disponibilidade = models.IntegerField()
    satisfacao_geral = models.IntegerField()

    # Comentário opcional
    comentario = models.TextField(null=True, blank=True)

    # Data da avaliação
    data = models.DateField(auto_now_add=True)

    # Nota final calculada automaticamente
    nota = models.FloatField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Substituindo campos None por 0 antes do cálculo
        self.rapidez_atendimento = self.rapidez_atendimento or 0
        self.eficiencia_resolucao = self.eficiencia_resolucao or 0
        self.clareza_comunicacao = self.clareza_comunicacao or 0
        self.profissionalismo = self.profissionalismo or 0
        self.suporte_gestao_pedidos = self.suporte_gestao_pedidos or 0
        self.proatividade = self.proatividade or 0
        self.disponibilidade = self.disponibilidade or 0
        self.satisfacao_geral = self.satisfacao_geral or 0

        # Calcula a média das avaliações e armazena em `nota`
        self.nota = (
            self.rapidez_atendimento + self.eficiencia_resolucao + self.clareza_comunicacao +
            self.profissionalismo + self.suporte_gestao_pedidos + self.proatividade +
            self.disponibilidade + self.satisfacao_geral
        ) / 8

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Avaliação de {self.colaborador} - Nota: {self.nota:.2f}"