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
            dias = hoje.day - self.data_contratacao.day

            # Ajuste se o mês atual é anterior ao mês de contratação ou dia anterior
            if meses < 0 or (meses == 0 and dias < 0):
                anos -= 1
                meses += 12

            if dias < 0:
                # Ajuste a quantidade de dias
                ultimo_dia_mes_anterior = (hoje.replace(day=1) - timedelta(days=1)).day
                dias += ultimo_dia_mes_anterior

            # Formatar a string de tempo
            partes_tempo = []
            if anos > 0:
                partes_tempo.append(f"{anos} anos")
            if meses > 0:
                partes_tempo.append(f"{meses} meses")
            if dias > 0:
                partes_tempo.append(f"{dias} dias")

            return ", ".join(partes_tempo) if partes_tempo else "Menos de 1 dia"
        
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


class Medalha(models.Model):
    colaborador = models.ForeignKey(Colaborador, related_name="medalhas", on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=0)  # Quantidade de medalhas
    tipo = models.CharField(max_length=100, blank=True, null=True)  # Tipo de medalha (opcional)
    descricao = models.TextField(blank=True, null=True)  # Descrição da medalha (opcional)

    def __str__(self):
        return f'{self.colaborador.nome} - {self.quantidade} medalhas'

    class Meta:
        verbose_name = "Medalha"
        verbose_name_plural = "Medalhas"


  

