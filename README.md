# PCP Komotors — Sistema de Gestão, Planejamento e Controle de Produção

Sistema web (Python/Django) para digitalizar e centralizar o planejamento,
controle e gestão da produção de baterias de chumbo-ácido para motocicletas.

> Documentação completa do produto: [`PRD.md`](PRD.md)
> Referência visual: [`@design_system/design-system.html`](@design_system/design-system.html)

## Status atual (Sprints 1 a 3)

- **Sprint 1 — Fundação:** infra, settings (django-environ, pt-br, America/Sao_Paulo),
  login por email, templates base aderentes ao design system, healthcheck.
- **Sprint 2 — Cadastros-base:** Operadores, Turnos (com flag "hora extra"),
  Setores, Máquinas, Modelos, Ligas, Motivos de parada; seed inicial de setores
  e ligas; admin completo.
- **Sprint 3 — Teleiras:** apontamentos de produção de grade com lote automático
  (001–999), filtros, permissões e média de produção por hora.

As tarefas concluídas estão marcadas com `[X]` na seção *12. Sprints de
implementação* do `PRD.md`.

## Como rodar localmente

Requisitos: Python 3.12+ (testado com 3.14).

```powershell
# 1. Criar ambiente virtual
py -3.14 -m venv .venv

# 2. Instalar dependências
& ".venv\Scripts\python.exe" -m pip install -r requirements.txt

# 3. Copiar .env
Copy-Item .env.example .env

# 4. Migrar (cria o banco SQLite e roda o seed de setores/ligas)
& ".venv\Scripts\python.exe" manage.py migrate

# 5. Criar superusuário (login por email)
& ".venv\Scripts\python.exe" -c "import os, django; os.environ['DJANGO_SETTINGS_MODULE']='core.settings'; django.setup(); from django.contrib.auth import get_user_model; get_user_model().objects.create_superuser(username='admin', email='admin@komotors.com', password='admin12345') if not get_user_model().objects.filter(username='admin').exists() else None"

# 6. Subir o servidor
& ".venv\Scripts\python.exe" manage.py runserver
```

Acesse:

- Sistema (login): http://localhost:8000/login/
- Dashboard: http://localhost:8000/
- Operadores: http://localhost:8000/operadores/
- Cadastros-base: http://localhost:8000/cadastros/
- Teleiras: http://localhost:8000/producao/teleiras/
- Django Admin: http://localhost:8000/admin/

### Login de teste
- **Email:** `admin@komotors.com`
- **Senha:** `admin12345`

### Dados de demonstração (seed)
- 7 setores: Teleiras, Boleira, Moinho, Masseira,Empastadeira, Montagem, Formação
- 4 ligas de chumbo com cores: Liga 0 (preto), Liga 4 (verde),
  Liga 5 (vermelho), Liga 6 (amarelo)

## Versionamento por sprint

Cada sprint foi commitada e marcada com uma tag Git para permitir análise
por partes:

| Tag              | Sprint                              |
|------------------|-------------------------------------|
| `v1.0.0-sprint1` | Sprint 1 — Fundação do projeto      |
| `v1.0.0-sprint2` | Sprint 2 — Cadastros-base           |
| `v1.0.0-sprint3` | Sprint 3 — Teleiras (apontamentos)  |

Para visualizar o estado de uma sprint específica:

```powershell
git checkout v1.0.0-sprint2   # analisa Sprint 1 + 2
git checkout main            # volta ao estado mais recente
```

## Arquitetura (resumo)

- **core** — settings, urls, asgi/wsgi, healthcheck
- **base** — recursos compartilhados (auth por email, models abstratos,
  mixins, templates base, template tags)
- **operators** — cadastro de operadores (UI "Operador")
- **catalogs** — cadastros-base: Turnos, Setores, Máquinas, Modelos,
  Ligas, Motivos de parada
- **production** — apontamentos de produção (Teleiras → GridProduction)

Próximas sprints (paradas de máquina, empaste, masseira, montagem,
formação, estoque de chumbo, contagem de grades, dashboard, relatórios,
IA, infra Docker) conforme o `PRD.md`.