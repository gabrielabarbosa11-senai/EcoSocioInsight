# Deploy SocioEcoInsight — VPS Ubuntu 24.04 LTS

> Stack: **Django 5** · **Gunicorn** · **Nginx** · **Certbot/Let's Encrypt** · **Supabase (PostgreSQL 16 + pgvector)** · **Groq API**

Plano de deploy seguro e performático. Substitua todos os placeholders `[...]` antes de executar.

---

## Premissas extraídas do projeto real

| Item | Valor mapeado |
|---|---|
| WSGI entry-point | `config.wsgi:application` |
| Settings module | `config.settings` |
| Static source | `presentation/static/` |
| Static root (collectstatic) | `staticfiles/` (definir no `.env`) |
| Env loader | `django-environ` via `environ.Env.read_env(BASE_DIR / '.env')` |
| Variáveis obrigatórias | `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `DATABASE_URL`, `GROQ_API_KEY`, `OPENAI_API_KEY` |

---

## ETAPA 1 — `setup.sh` · Script de Inicialização do Servidor

Copie para a VPS e execute como root: `bash setup.sh`

```bash
#!/usr/bin/env bash
# =============================================================================
# setup.sh — SocioEcoInsight · Deploy Inicial · Ubuntu 24.04 LTS
# Execute como root: bash setup.sh
# =============================================================================
set -euo pipefail   # Aborta em qualquer erro; variáveis não definidas causam erro

# -----------------------------------------------------------------------------
# 1. ATUALIZAR APT E INSTALAR DEPENDÊNCIAS DO SISTEMA
# -----------------------------------------------------------------------------
echo "[1/6] Atualizando pacotes do sistema..."
apt update && apt upgrade -y

echo "[2/6] Instalando dependências de sistema..."
apt install -y \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    libpq-dev \
    nginx \
    git \
    certbot \
    python3-certbot-nginx \
    ufw

# -----------------------------------------------------------------------------
# 2. CONFIGURAR FIREWALL (UFW)
# Permite apenas SSH, HTTP e HTTPS — bloqueia todo o resto.
# -----------------------------------------------------------------------------
echo "[3/6] Configurando UFW..."
ufw allow OpenSSH
ufw allow 'Nginx Full'   # Abre portas 80 (HTTP) e 443 (HTTPS)
ufw --force enable

# -----------------------------------------------------------------------------
# 3. CLONAR O REPOSITÓRIO
# Substitua [URL_DO_REPOSITORIO] pela URL real do seu repositório Git.
# Ex: https://github.com/seuusuario/SocioEcoInsight.git
# -----------------------------------------------------------------------------
echo "[4/6] Clonando repositório..."
APP_DIR="/opt/socioeco"
git clone [URL_DO_REPOSITORIO] "$APP_DIR"
cd "$APP_DIR"

# -----------------------------------------------------------------------------
# 4. CRIAR AMBIENTE VIRTUAL E INSTALAR DEPENDÊNCIAS PYTHON
# -----------------------------------------------------------------------------
echo "[5/6] Criando virtualenv e instalando requirements..."
python3 -m venv "$APP_DIR/venv"
source "$APP_DIR/venv/bin/activate"

# Atualiza pip e instala gunicorn + dependências do projeto
pip install --upgrade pip
pip install gunicorn
pip install -r "$APP_DIR/requirements.txt"

# -----------------------------------------------------------------------------
# 5. CRIAR O ARQUIVO .env
# ATENÇÃO: Nunca commite este arquivo no Git.
# Preencha TODOS os valores abaixo antes de continuar.
# -----------------------------------------------------------------------------
echo "[6/6] Gerando template do .env — EDITE ANTES DE CONTINUAR!"
cat > "$APP_DIR/.env" << 'EOF'
# =============================================
#  ATENÇÃO: Arquivo de segredos de produção.
#  Nunca versionar este arquivo.
# =============================================

# Django Core
SECRET_KEY=[GERE_UMA_SECRET_KEY_FORTE_AQUI]
DEBUG=False
ALLOWED_HOSTS=[SEU_DOMINIO_AQUI],www.[SEU_DOMINIO_AQUI]

# Banco de Dados — Supabase PostgreSQL 16
# Formato: postgres://usuario:senha@host:5432/nome_do_banco
DATABASE_URL=[SUA_DATABASE_URL_DO_SUPABASE_AQUI]

# Groq API
GROQ_API_KEY=[SUA_GROQ_API_KEY_AQUI]
GROQ_MODEL=llama-3.3-70b-versatile

# OpenAI (se utilizado como fallback no orchestrator)
OPENAI_API_KEY=[SUA_OPENAI_API_KEY_AQUI]

# Django Static Files (collectstatic output)
STATIC_ROOT=/opt/socioeco/staticfiles
EOF

echo "------------------------------------------------------------"
echo "  EDITE O ARQUIVO /opt/socioeco/.env com seus valores reais!"
echo "  Execute o próximo bloco SOMENTE após editar o .env."
echo "------------------------------------------------------------"

# -----------------------------------------------------------------------------
# 6. COLLECTSTATIC
# Execute manualmente APÓS editar o .env com os valores reais.
# -----------------------------------------------------------------------------
# source /opt/socioeco/venv/bin/activate
# cd /opt/socioeco
# python manage.py collectstatic --noinput

echo ""
echo "=== setup.sh concluído. Edite o .env e rode collectstatic. ==="
```

> [!IMPORTANT]
> Adicione `STATIC_ROOT` ao [settings.py](file:///g:/Antigravity%20Projects/SocioEcoInsight/config/settings.py) caso ainda não esteja definido:
> ```python
> STATIC_ROOT = BASE_DIR / env('STATIC_ROOT', default='staticfiles')
> ```

---

## ETAPA 2 — `/etc/systemd/system/gunicorn.service`

```ini
# =============================================================================
# gunicorn.service — SocioEcoInsight
# Gerencia o processo Gunicorn como serviço systemd
# Caminho: /etc/systemd/system/gunicorn.service
# =============================================================================

[Unit]
Description=Gunicorn WSGI daemon — SocioEcoInsight
# Sobe após a rede estar disponível (necessário para conexão com Supabase)
After=network.target

[Service]
# ---------------------------------------------------------------
# Usuário e grupo (evita rodar como root em produção real;
# se o Droplet usa root por padrão, troque para 'ubuntu' ou
# crie um usuário dedicado: adduser --system --no-create-home socioeco)
# ---------------------------------------------------------------
User=root
Group=www-data

# Diretório de trabalho (BASE_DIR do Django)
WorkingDirectory=/opt/socioeco

# ---------------------------------------------------------------
# Carrega todas as variáveis do .env antes de iniciar os workers.
# O Gunicorn herda o ambiente e o Django lê via django-environ.
# ---------------------------------------------------------------
EnvironmentFile=/opt/socioeco/.env

# Garante que o Django encontre as settings corretas
Environment="DJANGO_SETTINGS_MODULE=config.settings"

# ---------------------------------------------------------------
# Comando de inicialização do Gunicorn
# --workers: (2 * CPUs) + 1  →  3 para Droplet de 1 vCPU
#            Aumente para 5 em Droplets de 2 vCPUs.
# --bind: socket UNIX (mais rápido que TCP localhost para comunicação interna)
# --timeout: 120s para suportar chamadas longas à Groq API / pgvector
# --access-logfile / --error-logfile: logs persistentes
# ---------------------------------------------------------------
ExecStart=/opt/socioeco/venv/bin/gunicorn \
    config.wsgi:application \
    --workers 3 \
    --bind unix:/run/gunicorn.sock \
    --timeout 120 \
    --log-level info \
    --access-logfile /var/log/gunicorn/access.log \
    --error-logfile /var/log/gunicorn/error.log

# Cria /run/gunicorn.sock com permissões corretas para o Nginx
RuntimeDirectory=gunicorn
RuntimeDirectoryMode=0755

# Garante que o diretório de logs exista
ExecStartPre=/bin/mkdir -p /var/log/gunicorn

# Reinicialização automática em caso de falha
Restart=on-failure
RestartSec=5s

# Limites de segurança
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

---

## ETAPA 3 — `/etc/nginx/sites-available/socioecoinsight`

```nginx
# =============================================================================
# socioecoinsight — Nginx Server Block
# Caminho: /etc/nginx/sites-available/socioecoinsight
# ATENÇÃO: Substitua [SEU_DOMINIO_AQUI] pelo domínio real antes de ativar.
# O Certbot irá adicionar automaticamente o bloco HTTPS (porta 443) e
# redirecionar HTTP → HTTPS após rodar: certbot --nginx
# =============================================================================

upstream gunicorn_server {
    # Socket UNIX: comunicação zero-overhead entre Nginx e Gunicorn
    server unix:/run/gunicorn.sock fail_timeout=0;
}

server {
    listen 80;
    listen [::]:80;

    # ---------------------------------------------------------------
    # SUBSTITUA PELO SEU DOMÍNIO REAL
    # Exemplo: server_name socioecoinsight.com.br www.socioecoinsight.com.br;
    # ---------------------------------------------------------------
    server_name [SEU_DOMINIO_AQUI] www.[SEU_DOMINIO_AQUI];

    # ---------------------------------------------------------------
    # ARQUIVOS ESTÁTICOS — servidos diretamente pelo Nginx (sem bater no Gunicorn)
    # Aponta para o STATIC_ROOT gerado pelo collectstatic
    # ---------------------------------------------------------------
    location /static/ {
        alias /opt/socioeco/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # ---------------------------------------------------------------
    # ARQUIVOS DE MÍDIA — uploads de usuários (se aplicável)
    # ---------------------------------------------------------------
    location /media/ {
        alias /opt/socioeco/media/;
        expires 7d;
        add_header Cache-Control "public";
        access_log off;
    }

    # ---------------------------------------------------------------
    # PROXY REVERSO → Gunicorn via socket UNIX
    # ---------------------------------------------------------------
    location / {
        proxy_pass http://gunicorn_server;

        # Headers essenciais para o Django interpretar a requisição corretamente
        proxy_set_header Host              $http_host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Buffer e timeout para suportar respostas longas (RAG / Groq API)
        proxy_read_timeout   120s;
        proxy_connect_timeout 10s;
        proxy_send_timeout   120s;

        proxy_buffering          on;
        proxy_buffer_size        16k;
        proxy_buffers            8 16k;
        proxy_busy_buffers_size  32k;

        # Tamanho máximo de upload
        client_max_body_size 50M;
    }

    # ---------------------------------------------------------------
    # SEGURANÇA — Headers HTTP
    # ---------------------------------------------------------------
    add_header X-Content-Type-Options  "nosniff"          always;
    add_header X-Frame-Options         "DENY"             always;
    add_header Referrer-Policy         "strict-origin"    always;
}
```

---

## ETAPA 4 — Roteiro Final de Ativação

Execute os comandos na VPS **em sequência**, como root:

```bash
# =============================================================================
# ETAPA 4 — ATIVAÇÃO DO SERVIÇO
# =============================================================================

# --- [PRÉ-REQUISITO] Coletar estáticos antes de tudo ---
source /opt/socioeco/venv/bin/activate
cd /opt/socioeco
python manage.py collectstatic --noinput
deactivate

# --- 1. Ativar e iniciar o Gunicorn ---
systemctl daemon-reload
systemctl enable gunicorn     # Registra para subir automaticamente no boot
systemctl start  gunicorn     # Inicia agora

# Verificar se o socket foi criado corretamente:
ls -la /run/gunicorn.sock     # Deve aparecer: srwxr-xr-x ... /run/gunicorn.sock

# Verificar logs do serviço em caso de falha:
journalctl -u gunicorn -n 50 --no-pager

# --- 2. Ativar o site no Nginx (link simbólico) ---
ln -s /etc/nginx/sites-available/socioecoinsight \
      /etc/nginx/sites-enabled/socioecoinsight

# Remover o site padrão do Nginx (evita conflito de server_name)
rm -f /etc/nginx/sites-enabled/default

# Testar a sintaxe da configuração do Nginx (NUNCA pule este passo)
nginx -t

# --- 3. Reiniciar o Nginx ---
systemctl restart nginx
systemctl enable  nginx      # Garante que sobe automaticamente no boot

# Verificar status:
systemctl status nginx

# --- 4. Emitir certificado SSL com Certbot (Let's Encrypt) ---
# O Certbot detecta automaticamente os server_name do bloco Nginx,
# cria o certificado e reescreve o config para HTTPS (porta 443)
# com redirect permanente HTTP → HTTPS.
certbot --nginx \
    -d [SEU_DOMINIO_AQUI] \
    -d www.[SEU_DOMINIO_AQUI] \
    --non-interactive \
    --agree-tos \
    --email [SEU_EMAIL_AQUI] \
    --redirect

# Testar renovação automática (cron/timer já configurado pelo Certbot):
certbot renew --dry-run

# --- 5. Verificação final ---
# Deve retornar 301 → https://...
curl -I http://[SEU_DOMINIO_AQUI]

# Deve retornar 200 e a página da aplicação
curl -I https://[SEU_DOMINIO_AQUI]
```

---

## Checklist Pós-Deploy

| # | Verificação | Comando |
|---|---|---|
| 1 | Gunicorn ativo | `systemctl is-active gunicorn` |
| 2 | Socket existente | `ls /run/gunicorn.sock` |
| 3 | Nginx sem erros | `nginx -t` |
| 4 | HTTPS funcionando | `curl -I https://[SEU_DOMINIO]` |
| 5 | Certificado SSL válido | `certbot certificates` |
| 6 | Logs Gunicorn limpos | `tail -f /var/log/gunicorn/error.log` |
| 7 | Logs Nginx limpos | `tail -f /var/log/nginx/error.log` |

> [!WARNING]
> **Nunca coloque** `DEBUG=True` em produção. Confirme que o `.env` tem `DEBUG=False` antes de ativar o Gunicorn.

> [!IMPORTANT]
> O `settings.py` atual não define `STATIC_ROOT`. Adicione a linha antes do `collectstatic`:
> ```python
> STATIC_ROOT = BASE_DIR / 'staticfiles'
> ```

> [!TIP]
> Para verificar a saúde do deploy a qualquer momento: `systemctl status gunicorn nginx certbot.timer`