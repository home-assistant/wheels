ARG BUILD_FROM
FROM ${BUILD_FROM}

ARG \
    BUILD_ARCH \
    CPYTHON_ABI \
    QEMU_CPU \
    AUDITWHEEL_VERSION=5.1.2

WORKDIR /usr/src

SHELL ["/bin/bash", "-exo", "pipefail", "-c"]

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
            openblas-dev \
        && pip3 install --no-cache-dir \
            --extra-index-url "https://wheels.home-assistant.io/musllinux-index/" \
            git+https://github.com/scikit-build/ninja-python-distributions.git@89b1a02be6b47919c4da3daad06f2a020a16cc7f \
        && pip3 install --no-cache-dir \
            --extra-index-url "https://wheels.home-assistant.io/musllinux-index/" \
            Cython packaging patchelf pyproject-metadata setuptools \
        && pip3 install --no-cache-dir \
            --no-build-isolation \
            --extra-index-url "https://wheels.home-assistant.io/musllinux-index/" \
            $(cat /usr/src/requirements_${CPYTHON_ABI}.txt | grep numpy); \
    fi \
    && pip3 install --no-cache-dir \
        -r /usr/src/requirements.txt \
        -r /usr/src/requirements_${CPYTHON_ABI}.txt \
        --extra-index-url "https://wheels.home-assistant.io/musllinux-index/" \
    && rm -rf /usr/src/*

# Install auditwheel
COPY 0001-Support-musllinux-armv6l.patch /usr/src/
RUN \
    set -x \
    && git clone --depth 1 -b ${AUDITWHEEL_VERSION} \
        https://github.com/pypa/auditwheel \
    && cd auditwheel \
    && git apply /usr/src/0001-Support-musllinux-armv6l.patch \
    && pip install --no-cache-dir . \
    && rm -rf /usr/src/*

# Install builder
COPY . /usr/src/builder/
RUN \
    set -x \
    && pip3 install --no-cache-dir /usr/src/builder/ \
    && rm -rf /usr/src/*

# Set build environment information
ENV \
    ARCH=${BUILD_ARCH} \
    ABI=${CPYTHON_ABI}

# Runtime
WORKDIR /data
COPY rootfs /

ENTRYPOINT [ "run-builder.sh" ]
