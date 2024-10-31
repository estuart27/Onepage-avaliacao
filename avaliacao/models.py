# avaliacao/models.py
from django.db import models
from django.db import models
from django.core.files.base import ContentFile
from PIL import Image as PilImage
import io

class Colaborador(models.Model):
    # Definindo as opções de seleção para os cargos e hubs
    CARGO_CHOICES = [
        ('Líder de Logística', 'Líder de Logística'),
        ('Assistente de Logística', 'Assistente de Logística'),
        ('Mensageiro', 'Mensageiro'),
        ('Supervisor', 'Supervisor'),
        ('Staf', 'Staf'),

    ]

    HUB_CHOICES = [
        ('Shopping Boulevard', 'Shopping Boulevard'),
        ('Aurora Shopping', 'Aurora Shopping'),
    ]
    
    nome = models.CharField(max_length=100)
    cargo = models.CharField(max_length=100, choices=CARGO_CHOICES, null=True)  # Permitir nulo
    data_contratacao = models.DateField()  # Este campo está correto
    imagem = models.ImageField(upload_to='media/')
    hub = models.CharField(max_length=255, choices=HUB_CHOICES, null=True, blank=True)  # Permitir nulo e vazio

    def save(self, *args, **kwargs):
        # Redimensionar a imagem
        if self.imagem:
            img = PilImage.open(self.imagem)
            img = img.convert('RGB')  # Converter para RGB se a imagem for PNG
            
            # Redimensionar a imagem para 300x200
            img = img.resize((816, 816), PilImage.LANCZOS)  # Usar LANCZOS para suavização

            # Salvar a imagem redimensionada em um buffer
            img_io = io.BytesIO()
            img.save(img_io, format='JPEG', quality=85)  # Salvar como JPEG
            img_file = ContentFile(img_io.getvalue(), name=self.imagem.name)
            self.imagem = img_file

        super().save(*args, **kwargs)


class Avaliacao(models.Model):
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



  
