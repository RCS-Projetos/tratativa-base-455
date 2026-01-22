# --- ETAPA 1: Builder (Instalação de Libs com UV) ---
FROM python:3.11-slim AS builder

# 1. Instala o UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# 2. Configura o UV para criar o venv na pasta local
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/app/.venv

WORKDIR /app

# 3. Copia arquivos de dependência
COPY pyproject.toml uv.lock ./

# 4. Instala dependências (cria a pasta .venv)
# --frozen: usa versões exatas do lockfile
# --no-install-project: não instala o seu código ainda, só as libs
RUN uv sync --frozen --no-install-project --no-dev


# --- ETAPA 2: Runner (Imagem Final com Chrome) ---
FROM python:3.11-slim

WORKDIR /app

# 1. Instalação do Google Chrome (Essencial para o Robô)
RUN apt-get update && apt-get install -y \
    wget gnupg unzip curl \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# 2. Copia o ambiente virtual da etapa anterior
COPY --from=builder /app/.venv /app/.venv

# 3. Adiciona o venv ao PATH
# Isso faz com que o comando "python" ou "uvicorn" use o venv automaticamente
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

# 4. Copia o código fonte do Robô
COPY . .

# 5. Comando de inicialização
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]