FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml .
COPY brain ./brain
ENV PORT=8080
EXPOSE 8080
CMD ["python", "-m", "brain", "serve", "/data"]
