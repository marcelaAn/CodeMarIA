# Use uma imagem base do Python
FROM python:3.9-slim

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos de requisitos
COPY requirements.txt .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código fonte
COPY code_maria/ code_maria/
COPY data/ data/
COPY notebooks/ notebooks/

# Define variáveis de ambiente
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expõe a porta (se necessário para API)
EXPOSE 8000

# Comando para executar a aplicação
CMD ["python", "-m", "code_maria.core"] 