from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, CreateView, UpdateView, DetailView, DeleteView
from django.http import JsonResponse, HttpResponseForbidden
from .models import Activity, ActivityLog, User
from .forms import LoginForm, ActivityForm, ActivityLogForm
from .servicos.senior import start_workflow
from django.contrib import messages
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from django.utils.dateparse import parse_datetime
from django.utils import timezone
import datetime

# DRF
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import ActivitySerializer, ActivityLogSerializer, UserPublicSerializer
from .permissions import IsProjectManager

class LoginView(View):
    def get(self, request):
        form = LoginForm()
        return render(request, "core/login.html", {"form": form})
    def post(self, request):
        form = LoginForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect("home")
        return render(request, "core/login.html", {"form": form})


class LogoutView(View):
    def post(self, request):
        logout(request)
        return redirect("login")

class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "core/calendar.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.user.gerente_projetos:
            ctx["usuarios"] = User.objects.all()
        return ctx

class ManagerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.gerente_projetos
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return HttpResponseForbidden("Acesso restrito a Gerentes de Projetos.")
        return super().handle_no_permission()

class ActivityCreateView(LoginRequiredMixin, ManagerRequiredMixin, CreateView):
    model = Activity
    form_class = ActivityForm
    template_name = "core/activity_form.html"
    success_url = reverse_lazy("home")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user  # passa o usuário logado pro form
        return kwargs

    def form_valid(self, form):
        form.instance.criado_por = self.request.user
        return super().form_valid(form)


class ActivityStartWorkflowView(LoginRequiredMixin, ManagerRequiredMixin, View):
    pk_url_kwarg = "numero"

    @method_decorator(require_POST)  # força POST (boa prática)
    def post(self, request, numero):
        atividade = get_object_or_404(Activity, pk=numero)

        try:
            result = start_workflow(atividade)
            messages.success(request, "BPM gerado com sucesso!")
        except Exception as e:
            messages.error(request, f"Erro ao gerar o BPM: {e}")

        return redirect("activity_detail", numero=numero)    

class ActivityUpdateView(LoginRequiredMixin, ManagerRequiredMixin, UpdateView):
    model = Activity
    form_class = ActivityForm
    template_name = "core/activity_form.html"
    success_url = reverse_lazy("home")
    pk_url_kwarg = "numero"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user  # passa o usuário logado para o form
        return kwargs


class ActivityDetailView(LoginRequiredMixin, DetailView):
    model = Activity
    template_name = "core/activity_detail.html"
    pk_url_kwarg = "numero"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["log_form"] = ActivityLogForm()
        return ctx
    
class ActivityDeleteView(LoginRequiredMixin, ManagerRequiredMixin, DeleteView):
    model = Activity
    template_name = "core/activity_confirm_delete.html"
    success_url = reverse_lazy("home")
    pk_url_kwarg = "numero"

class LogCreateView(LoginRequiredMixin, View):
    def post(self, request, numero):
        atividade = get_object_or_404(Activity, pk=numero)
        
        if not (request.user.gerente_projetos or atividade.recurso_id == request.user.id):
            return HttpResponseForbidden("Você não possui permissão para apontar nesta atividade.")
        form = ActivityLogForm(request.POST)
        if form.is_valid():
            log = form.save(commit=False)
            log.usuario = request.user
            log.atividade = atividade
            log.save()
            return redirect("activity_detail", numero=atividade.numero)
        return render(request, "core/activity_detail.html", {"object": atividade, "log_form": form})

User = get_user_model()

class ActivityFeedView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        usuario_alvo = user  

        # gerente pode trocar de agenda
        if user.gerente_projetos and "user_id" in request.GET:
            usuario_alvo = get_object_or_404(User, id=request.GET["user_id"])

        qs = Activity.objects.filter(recurso=usuario_alvo)

        # pegar intervalo enviado pelo FullCalendar
        start_param = request.GET.get('start')
        end_param = request.GET.get('end')

        if start_param and end_param:
            try:
                # converter ISO string para timezone-aware
                start_dt = datetime.datetime.fromisoformat(start_param.replace('Z', '+00:00'))
                end_dt = datetime.datetime.fromisoformat(end_param.replace('Z', '+00:00'))
                start_dt = timezone.make_aware(start_dt)
                end_dt = timezone.make_aware(end_dt)
                # filtrar eventos que intersectam o período
                qs = qs.filter(
                    inicio_previsto__lt=end_dt
                ).filter(
                    fim_previsto__gt=start_dt
                ) | qs.filter(
                    fim_previsto__isnull=True,
                    inicio_previsto__lt=end_dt
                )
            except Exception as e:
                print("Erro ao converter datas:", e)

        events = []
        for a in qs:
            inicio = timezone.localtime(a.inicio_previsto)
            fim = timezone.localtime(a.fim_previsto) if a.fim_previsto else (inicio + datetime.timedelta(hours=1))
            events.append({
                "id": a.numero,
                "title": f"#{a.numero} {a.nome_cliente} ({a.numero_orcamento})",
                "start": inicio.isoformat(),
                "end": fim.isoformat(),
                "allDay": False,
                "extendedProps": {
                    "cliente": a.nome_cliente,
                    "orcamento": a.numero_orcamento,
                    "recurso": str(a.recurso),
                    "criado_por": str(a.criado_por),
                },
                "color": "#0d6efd" if a.recurso_id == user.id else "#6c757d",
            })

        return JsonResponse(events, safe=False)
    
# --- DRF ViewSets ---
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all().order_by("username")
    serializer_class = UserPublicSerializer
    permission_classes = [permissions.IsAuthenticated]

class ActivityViewSet(viewsets.ModelViewSet):
    queryset = Activity.objects.select_related("recurso","criado_por").all()
    serializer_class = ActivitySerializer
    permission_classes = [permissions.IsAuthenticated & IsProjectManager]

    def perform_create(self, serializer):
        serializer.save(criado_por=self.request.user)

class ActivityLogViewSet(viewsets.ModelViewSet):
    queryset = ActivityLog.objects.select_related("atividade","usuario").all()
    serializer_class = ActivityLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        atividade = serializer.validated_data["atividade"]
        u = self.request.user
        if not (u.gerente_projetos or atividade.recurso_id == u.id):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Sem permissão para apontar nesta atividade.")
        serializer.save(usuario=u)
