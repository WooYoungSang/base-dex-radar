FROM nvidia/cuda:12.6.3-runtime-ubuntu22.04 AS cuda-libs

FROM python:3.11-slim
# Copy only the CUDA runtime shared library needed for ctypes
COPY --from=cuda-libs /usr/local/cuda-12.6/targets/x86_64-linux/lib/libcudart.so.12 /usr/local/lib/libcudart.so.12
RUN ln -s /usr/local/lib/libcudart.so.12 /usr/local/lib/libcudart.so && ldconfig
WORKDIR /app
COPY pyproject.toml .
COPY src/ src/
RUN pip install --no-cache-dir .
# CUDA Bellman-Ford shared library (compiled for sm_89 / RTX 4090)
COPY libbellman.so .
EXPOSE 8000
CMD ["uvicorn", "dex_radar.api:app", "--host", "0.0.0.0", "--port", "8000"]
