FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    CODEX_ONES_SYNTHETIC_ONLY=1 \
    MCP_ALLOWED_HOSTS=localhost,localhost:*,127.0.0.1,127.0.0.1:*

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
RUN python -m pip install --no-cache-dir .

COPY mcp-server/pyproject.toml ./mcp-server/pyproject.toml
COPY mcp-server/src ./mcp-server/src
RUN python -m pip install --no-cache-dir ./mcp-server

EXPOSE 8000

CMD ["python", "-m", "university_insights_mcp.server", "--transport", "http", "--host", "0.0.0.0", "--port", "8000"]
