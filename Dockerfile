FROM grafana/k6:latest

# Metadata
LABEL maintainer="GhostNoc99"
LABEL description="k6 performance testing image"
LABEL version="1.0"

# Directorio de trabajo
WORKDIR /k6

# Copiar script de prueba
COPY k6/dynamic-test.js .

# Directorio para reportes
RUN mkdir -p /k6/reports

# Volumen para reportes
VOLUME ["/k6/reports"]

# Entrypoint por defecto
ENTRYPOINT ["k6"]
CMD ["--help"]