FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

# seed.py usa los binarios de Info-ZIP: zipfile no escribe archivos con clave.
RUN apt-get update && apt-get install -y --no-install-recommends \
      zip unzip && rm -rf /var/lib/apt/lists/*

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# El venv en PATH evita que uv necesite escribir como usuario no-root.
ENV PATH="/app/.venv/bin:$PATH"

COPY app.py content.py messages.py seed.py schema.sql ./
COPY templates ./templates
COPY static ./static
# seed.py arma los adjuntos con estas imagenes; sin ellas falla al arrancar.
COPY assets ./assets
COPY entrypoint.sh ./

RUN useradd --create-home challenge \
 && chmod +x entrypoint.sh \
 && chown -R challenge:challenge /app
USER challenge

ENV PORT=8080
EXPOSE 8080
ENTRYPOINT ["./entrypoint.sh"]
