ARG BUILD_FROM
FROM ${BUILD_FROM}

ARG \
    BUILD_ARCH \
    CPYTHON_ABI \
    QEMU_CPU \
    AUDITWHEEL_VERSION=6.4.2 \
    UV_SYSTEM_PYTHON=true \
    UV_EXTRA_INDEX_URL="https://wheels.home-assistant.io/musllinux-index/" \
    PIP_EXTRA_INDEX_URL=https://wheels.home-assistant.io/musllinux-index/

WORKDIR /usr/src

SHELL ["/bin/bash", "-exo", "pipefail", "-c"]

COPY rootfs /

# Uv is only needed during build
RUN --mount=from=ghcr.io/astral-sh/uv:0.9.7,source=/uv,target=/bin/uv \
    # Uv creates a lock file in /tmp
    --mount=type=tmpfs,target=/tmp \
    --mount=type=bind,source=.,target=/usr/src/builder/ \
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
    && if [ "${BUILD_ARCH}" = "i386" ]; then \
        export NPY_DISABLE_SVML=1; \
    fi \
    && if [ "${CPYTHON_ABI}" = "cp312" ] && [ "${BUILD_ARCH}" != "amd64" ]; then \
        apk add --no-cache --virtual .build-dependencies2 \
            openblas-dev; \
    fi \
    && uv sync --locked --group cp --no-install-project \
    && git clone --depth 1 -b ${AUDITWHEEL_VERSION} \
        https://github.com/pypa/auditwheel \
    && cd auditwheel \
    && git apply /usr/src/0001-Support-musllinux-armv6l.patch \
    && uv sync --locked

# Set build environment information
ENV \
    ARCH=${BUILD_ARCH} \
    ABI=${CPYTHON_ABI}

# Runtime
WORKDIR /data

ENTRYPOINT [ "run-builder.sh" ]
