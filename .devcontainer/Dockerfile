FROM mcr.microsoft.com/devcontainers/python:3.12

WORKDIR /workspace

# Install Python dependencies from requirements.txt if it exists
COPY requirements.txt requirements_tests.txt /tmp/pip-tmp/
RUN \
    pip install -r /tmp/pip-tmp/requirements.txt \
    && pip3 install -r /tmp/pip-tmp/requirements_tests.txt \
    && pip install tox \
    && rm -rf /tmp/pip-tmp/
