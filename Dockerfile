# Rilavo Protocol — hosted service + CLI image.
# Multi-stage: build the wheel with uv, install into a slim runtime.
FROM python:3.12-slim AS builder
WORKDIR /build
RUN pip install --no-cache-dir uv
COPY pyproject.toml README.md ./
COPY src ./src
RUN uv pip install --system --no-cache . 

FROM python:3.12-slim AS runtime
RUN useradd --create-home --shell /usr/sbin/nologin rilavo
WORKDIR /home/rilavo
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin/rilavo /usr/local/bin/rilavo
COPY --from=builder /usr/local/bin/rilavo-service /usr/local/bin/rilavo-service
COPY --from=builder /usr/local/bin/rilavo-conformance /usr/local/bin/rilavo-conformance
USER rilavo
ENV PORT=8090
EXPOSE 8090
# Default: hosted service. Override for CLI use:
#   docker run --rm rilavo-protocol rilavo --help
ENTRYPOINT ["rilavo-service"]
