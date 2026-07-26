FROM python:3.13-slim

# curl + unzip are used to refresh source/ from eBible.org; gnupg verifies
# the signature files shipped alongside the USFM sources.
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl unzip gnupg \
    && rm -rf /var/lib/apt/lists/*

# pyyaml: the notes/suggestions/ review files are YAML
RUN pip install --no-cache-dir --root-user-action=ignore pyyaml

WORKDIR /work
CMD ["/bin/bash"]
