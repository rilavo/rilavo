# Rilavo hosted issuance/verification service (P-31 path 3).
FROM python:3.12-slim

WORKDIR /app
RUN pip install --no-cache-dir uv

COPY pyproject.toml README.md ./
COPY src ./src
RUN uv pip install --system --no-cache .

EXPOSE 8090
# Runs the existing protocol HTTP service (the same two-call API surface).
CMD ["python", "-c", "from rilavo.service import RilavoService; import threading; s = RilavoService(port=8090).start(); print('hosted issuer live on', s.url, flush=True); threading.Event().wait()"]
