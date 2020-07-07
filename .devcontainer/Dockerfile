FROM mcr.microsoft.com/vscode/devcontainers/python:0-3.8

WORKDIR /workspace

# Install Python dependencies from requirements.txt if it exists
COPY requirements.txt requirements_tests.txt /workspace/
RUN pip install -r requirements.txt \
    && pip3 install -r requirements_tests.txt \
    && pip install tox
