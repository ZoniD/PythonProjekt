FROM python:3.14-slim

# Hent uv ind i image'et
COPY --from=ghcr.io/astral-sh/uv:0.12.6 /uv /bin/uv

WORKDIR /app

# Installer afhængigheder først, så Docker kan cache dette lag
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

# Kopiér resten af koden (.venv er udelukket via .dockerignore)
COPY . .

# Hvilken kommando der køres (API eller frontend) bestemmes i docker-compose.yml
