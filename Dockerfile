FROM fedora:latest
LABEL \
    name="Microservice to merge modulemd documents" \
    vendor="Factory 2.0 developers" \
    license="GPLv2+" \
    build-date=""

RUN dnf -y update && dnf -y install \
    python3-gunicorn \
    python3-flask \
    python3-modulemd \
    && dnf -y clean all

COPY modulemd-merger.py .

USER 1001
EXPOSE 8080

CMD ["/usr/bin/gunicorn-3", "--bind", "0.0.0.0:8080", "--access-logfile", "-", "--enable-stdio-inheritance", "modulemd-merger:app"]
