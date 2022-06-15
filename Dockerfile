ARG BUILD_FROM
FROM ${BUILD_FROM}

ARG \
    BUILD_ARCH \
    CPYTHON_ABI \
    QEMU_CPU \
    AUDITWHEEL_VERSION=5.1.2 \

WORKDIR /usr/src

# Install requirements
COPY \
    requirements.txt \
    requirements_${CPYTHON_ABI} \
    /usr/src/
RUN \
    set -x \
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
    && pip3 install --no-cache-dir --find-links \
        "https://wheels.home-assistant.io/musllinux/" \
        -r requirements.txt \
        -r requirements_${CPYTHON_ABI}.txt \
    && rm -f *.txt

# Install auditwheel
COPY 0001-Support-musllinux-armv6l.patch /usr/src/
RUN \
    set -x \
    && git clone --depth 1 -b ${AUDITWHEEL_VERSION} \
        https://github.com/pypa/auditwheel \
    && cd auditwheel \
    && git apply ../0001-Support-musllinux-armv6l.patch \
    && pip install --no-cache-dir . \
    && rm -rf /usr/src/*

# Install builder
COPY . /usr/src/builder/
RUN \
    set -x \
    && pip3 install --no-cache-dir builder/ \
    && rm -fr builder

# Runtime
WORKDIR /data
ENV ARCH=${BUILD_ARCH}
ENTRYPOINT [ "python3", "-m", "builder" ]
