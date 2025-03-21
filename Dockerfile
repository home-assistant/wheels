ARG BUILD_FROM
FROM ${BUILD_FROM}

ARG \
    BUILD_ARCH \
    CPYTHON_ABI \
    QEMU_CPU \
    AUDITWHEEL_VERSION=6.2.0 \
    PIP_EXTRA_INDEX_URL=https://wheels.home-assistant.io/musllinux-index/

WORKDIR /usr/src

SHELL ["/bin/bash", "-exo", "pipefail", "-c"]

COPY rootfs /

# Install requirements
COPY \
    requirements.txt \
    requirements_${CPYTHON_ABI}.txt \
    /usr/src/
RUN \
    apk add --no-cache \
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
    && pip3 install \
        -r /usr/src/requirements.txt \
        -r /usr/src/requirements_${CPYTHON_ABI}.txt \
    && rm -rf /usr/src/*

# Install auditwheel
COPY 0001-Support-musllinux-armv6l.patch /usr/src/
RUN \
    set -x \
    && git clone --depth 1 -b ${AUDITWHEEL_VERSION} \
        https://github.com/pypa/auditwheel \
    && cd auditwheel \
    && git apply /usr/src/0001-Support-musllinux-armv6l.patch \
    && pip install . \
    && rm -rf /usr/src/*

# Install builder
COPY . /usr/src/builder/
RUN \
    set -x \
    && pip3 install /usr/src/builder/ \
    && rm -rf /usr/src/*

# Set build environment information
ENV \
    ARCH=${BUILD_ARCH} \
    ABI=${CPYTHON_ABI}

# Runtime
WORKDIR /data

ENTRYPOINT [ "run-builder.sh" ]
