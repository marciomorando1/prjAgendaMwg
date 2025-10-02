from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils import timezone
from .models import Activity, ActivityLog, User

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Usuário", widget=forms.TextInput(attrs={"class":"form-control"}))
    password = forms.CharField(label="Senha", widget=forms.PasswordInput(attrs={"class":"form-control"}))

class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ["numero_orcamento","nome_cliente","descricao","anexo",
                  "inicio_previsto","fim_previsto","recurso","servico"]
        widgets = {
            "numero_orcamento": forms.TextInput(attrs={"class":"form-control"}),
            "nome_cliente": forms.TextInput(attrs={"class":"form-control"}),
            "servico": forms.TextInput(attrs={"class":"form-control"}),
            "descricao": forms.Textarea(attrs={"class":"form-control","rows":3}),
            "anexo": forms.ClearableFileInput(attrs={"class":"form-control"}),
            "inicio_previsto": forms.DateTimeInput(attrs={"type":"datetime-local","class":"form-control"}),
            "fim_previsto": forms.DateTimeInput(attrs={"type":"datetime-local","class":"form-control"}),
            "recurso": forms.Select(attrs={"class":"form-select"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)  
        super().__init__(*args, **kwargs)

        if user and not user.gerente_projetos:
            # usuário comum só pode criar atividade para ele mesmo
            self.fields["recurso"].queryset = User.objects.filter(id=user.id)
            self.fields["recurso"].initial = user
            self.fields["recurso"].disabled = True


class ActivityLogForm(forms.ModelForm):
    class Meta:
        model = ActivityLog
        fields = ["inicio","fim","descricao"]
        widgets = {
            "inicio": forms.DateTimeInput(attrs={"type":"datetime-local","class":"form-control"}),
            "fim": forms.DateTimeInput(attrs={"type":"datetime-local","class":"form-control"}),
            "descricao": forms.Textarea(attrs={"class":"form-control","rows":3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        now = timezone.now().replace(second=0, microsecond=0)  # limpa segundos para caber no datetime
        self.fields["inicio"].initial = now
        self.fields["fim"].initial = now
