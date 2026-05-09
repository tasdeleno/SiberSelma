# Multi-stage build: küçük, root olmayan, distroless final image
FROM python:3.12-slim AS build

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

COPY server.py api_server.py web_ui.py ingest.py ./
COPY docs/wiki ./docs/wiki

# wiki.db'yi build sırasında oluştur (image içinde hazır gelsin)
RUN python ingest.py


FROM gcr.io/distroless/python3-debian12:nonroot

WORKDIR /app
COPY --from=build /install /usr/local
COPY --from=build /app /app

# 8765 = api_server, 8766 = web_ui
EXPOSE 8765 8766

# Default: MCP server (stdio). Override için:
#   docker run --rm -p 8765:8765 sibrselma python api_server.py
#   docker run --rm -p 8766:8766 sibrselma python web_ui.py
ENTRYPOINT ["python"]
CMD ["server.py"]
