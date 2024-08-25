# Use uma imagem base
FROM python:3.9-slim

# Instale dependências
RUN apt-get update && \
    apt-get install -y curl apt-transport-https ca-certificates gnupg sudo bash && \
    apt-get update

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN python3 -m pip install --upgrade pip

RUN python3 -m pip install --no-cache-dir -r requirements.txt

COPY app /usr/src/app
COPY users.json ./

# Defina variáveis de ambiente diretamente
ENV DISCORD_TOKEN=your-token
ENV TIMEOUT=60
ENV CHANNEL_NAME=cypher-watch
ENV GUILD_ID=your-guild-id
ENV DRY_RUN=False
ENV API_KEYS=your-API_KEYs
ENV API_KEY=your-API_KEY

ENTRYPOINT ["python3"]
CMD ["./main.py"]
