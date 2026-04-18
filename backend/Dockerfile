FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml .
COPY src/ src/
RUN pip install --no-cache-dir .
# CUDA Bellman-Ford shared library (compiled for sm_89 / RTX 4090)
COPY libbellman.so .
EXPOSE 8000
CMD ["uvicorn", "dex_radar.api:app", "--host", "0.0.0.0", "--port", "8000"]
