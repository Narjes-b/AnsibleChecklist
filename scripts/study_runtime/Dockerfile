FROM python:3.14-slim@sha256:9aaa474097d094040649f2162a627c0049b408f52138d980916788d80f04802f
RUN pip install --no-cache-dir ansible-core==2.21.0 PyYAML==6.0.3
COPY scripts/llm_behavior_checks.py /worker.py
ENV PYTHONDONTWRITEBYTECODE=1
WORKDIR /tmp
