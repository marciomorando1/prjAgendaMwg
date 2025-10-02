from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsProjectManager(BasePermission):
    message = "Apenas Gerentes de Projetos podem criar/alterar atividades."
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.gerente_projetos)

class IsResourceOrManager(BasePermission):
    message = "Apenas o recurso da atividade ou um gerente pode registrar apontamentos."
    def has_object_permission(self, request, view, obj):
        u = request.user
        return bool(u and u.is_authenticated and (u.gerente_projetos or obj.usuario_id == u.id))
