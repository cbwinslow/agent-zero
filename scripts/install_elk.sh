#!/bin/bash
set -euo pipefail

# Simple docker compose for ELK stack
if [[ ! -d deploy/elk ]]; then
    mkdir -p deploy/elk
fi

cat > deploy/elk/docker-compose.yml <<'YAML'
version: '3'
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.14.0
    environment:
      - discovery.type=single-node
    ports:
      - "9200:9200"
  kibana:
    image: docker.elastic.co/kibana/kibana:8.14.0
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch
YAML

docker compose -f deploy/elk/docker-compose.yml up -d
