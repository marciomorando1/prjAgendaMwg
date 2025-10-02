from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.core.validators import FileExtensionValidator

class User(AbstractUser):
    nome = models.CharField(max_length=150, blank=True)
    gerente_projetos = models.BooleanField(default=False)

    def __str__(self):
        return self.nome or self.get_full_name() or self.username

class Activity(models.Model):
    numero = models.AutoField(primary_key=True)  # Número da Atividade (sequencial automático)
    numero_orcamento = models.CharField(max_length=50)
    nome_cliente = models.CharField(max_length=120)
    servico = models.CharField(max_length=120, blank=True)
    descricao = models.TextField(blank=True)
    anexo = models.FileField(upload_to="anexos/", blank=True, null=True,
                             validators=[FileExtensionValidator(allowed_extensions=[
                                 "pdf","doc","docx","xls","xlsx","png","jpg","jpeg","txt"])]
                             )
    inicio_previsto = models.DateTimeField()
    fim_previsto = models.DateTimeField()
    recurso = models.ForeignKey(User, on_delete=models.PROTECT, related_name="atividades")
    criado_por = models.ForeignKey(User, on_delete=models.PROTECT, related_name="atividades_criadas")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["inicio_previsto"]

    def __str__(self):
        return f"Atv #{self.numero_orcamento} - {self.nome_cliente}"

    @property
    def duracao_prevista(self):
        return self.fim_previsto - self.inicio_previsto

    @property
    def minutos_previstos(self):
        return max(int(self.duracao_prevista.total_seconds() // 60), 0)

    @property
    def minutos_apontados(self):
        total = 0
        for log in self.logs.all():
            if log.inicio and log.fim and log.fim > log.inicio:
                total += int((log.fim - log.inicio).total_seconds() // 60)
        return total

class ActivityLog(models.Model):
    atividade = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name="logs")
    usuario = models.ForeignKey(User, on_delete=models.PROTECT)
    inicio = models.DateTimeField(default=timezone.now)
    fim = models.DateTimeField(blank=True, null=True)
    descricao = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em"]

    def __str__(self):
        return f"Apontamento {self.usuario} - {self.atividade}"
