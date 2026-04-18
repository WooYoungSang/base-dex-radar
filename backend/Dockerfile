FROM nvidia/cuda:12.6.3-runtime-ubuntu22.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y python3.11 python3-pip python3.11-venv && \
    ln -sf /usr/bin/python3.11 /usr/bin/python3 && \
    ln -sf /usr/bin/python3.11 /usr/bin/python && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY pyproject.toml .
COPY src/ src/
RUN pip install --no-cache-dir .
# CUDA Bellman-Ford shared library (compiled for sm_89 / RTX 4090)
COPY libbellman.so .
EXPOSE 8000
CMD ["uvicorn", "dex_radar.api:app", "--host", "0.0.0.0", "--port", "8000"]
