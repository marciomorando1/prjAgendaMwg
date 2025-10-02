# Calendário de Atividades (Django + SQLite)

Sistema básico de calendário para gerenciamento de tarefas por Gerentes de Projetos.

## Requisitos
- Python 3.11+
- Pip / venv

## Setup rápido
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Acesse: http://127.0.0.1:8000

## Perfis e Permissões
- `User.gerente_projetos = True` pode criar/editar atividades.
- Recurso (usuário atribuído) pode registrar apontamentos em sua atividade.

## API (DRF)
- `/api/users/` (GET)
- `/api/activities/` (CRUD) — protegido, apenas gerente cria/edita.
- `/api/logs/` (CRUD) — recurso ou gerente pode criar.

## MongoDB (Opcional)
- Instale `djongo` **ou** `mongoengine` e ajuste `settings.py` conforme comentários.

## Uploads
- Arquivos são guardados em `media/anexos/` (local). Configure S3 se desejar.
