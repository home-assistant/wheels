ARG BUILD_FROM
FROM ${BUILD_FROM}

ARG \
    BUILD_ARCH \
    CPYTHON_ABI \
    AUDITWHEEL_VERSION=6.4.2 \
    PIP_EXTRA_INDEX_URL=https://wheels.home-assistant.io/musllinux-index/

WORKDIR /usr/src

SHELL ["/bin/bash", "-exo", "pipefail", "-c"]

# Set build environment information
ENV \
    BUILD_ARCH=${BUILD_ARCH} \
    CPYTHON_ABI=${CPYTHON_ABI} \
    UV_SYSTEM_PYTHON=true \
    UV_EXTRA_INDEX_URL=${PIP_EXTRA_INDEX_URL} \
    UV_PROJECT_ENVIRONMENT=/usr/local

COPY rootfs /

# Uv is only needed during build
RUN --mount=from=ghcr.io/astral-sh/uv:latest,source=/uv,target=/bin/uv \
    # Uv creates a lock file in /tmp
    --mount=type=tmpfs,target=/tmp \
    --mount=type=bind,source=.,target=/usr/src/builder/,rw \
    apk upgrade --no-cache \
    && apk add --no-cache \
        rsync \
        openssh-client \
        patchelf \
        build-base \
        cmake \
        git \
        linux-headers \
        autoconf \
        automake \
        cargo \
        libffi \
    && apk add --no-cache --virtual .build-dependencies \
        libffi-dev \
    && uv sync --locked --project /usr/src/builder/ --group ${CPYTHON_ABI} \
    && git clone --depth 1 -b ${AUDITWHEEL_VERSION} \
        https://github.com/pypa/auditwheel \
    && cd auditwheel \
    && uv pip install .

# Runtime
WORKDIR /data

ENTRYPOINT [ "run-builder.sh" ]
