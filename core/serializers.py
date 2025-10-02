from rest_framework import serializers
from .models import User, Activity, ActivityLog

class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id","username","nome","email","gerente_projetos"]

class ActivitySerializer(serializers.ModelSerializer):
    recurso = UserPublicSerializer(read_only=True)
    recurso_id = serializers.PrimaryKeyRelatedField(source="recurso", queryset=User.objects.all(), write_only=True)
    criado_por = UserPublicSerializer(read_only=True)
    # percentual_concluido = serializers.IntegerField(read_only=True)

    class Meta:
        model = Activity
        fields = ["numero","numero_orcamento","nome_cliente","descricao","anexo",
                  "inicio_previsto","fim_previsto","recurso","recurso_id","criado_por,servico",
                ]

class ActivityLogSerializer(serializers.ModelSerializer):
    usuario = UserPublicSerializer(read_only=True)
    atividade_id = serializers.PrimaryKeyRelatedField(source="atividade", queryset=Activity.objects.all(), write_only=True)

    class Meta:
        model = ActivityLog
        fields = ["id","atividade","atividade_id","usuario","inicio","fim","descricao"]
        read_only_fields = ["atividade","usuario"]
