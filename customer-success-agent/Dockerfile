FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY agent.py config.py run_benchmark.py chat.html favicon.ico ./
COPY wiki /app/wiki
COPY mastersheet /app/mastersheet
COPY benchmarks /app/benchmarks
RUN mkdir -p /app/outputs /app/traces
EXPOSE 8000
CMD ["python", "agent.py", "--serve"]
