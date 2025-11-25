ARG BUILD_FROM
FROM ${BUILD_FROM}

ARG \
    BUILD_ARCH \
    CPYTHON_ABI \
    AUDITWHEEL_VERSION=6.5.0 \
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
    && pip3 install \
        -r /usr/src/requirements.txt \
        -r /usr/src/requirements_${CPYTHON_ABI}.txt \
    && rm -rf /usr/src/*

# Install auditwheel
RUN \
    set -x \
    && git clone --depth 1 -b ${AUDITWHEEL_VERSION} \
        https://github.com/pypa/auditwheel \
    && cd auditwheel \
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
