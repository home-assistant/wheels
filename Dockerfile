ARG BUILD_FROM
FROM ${BUILD_FROM}

ARG BUILD_ARCH
ENV ARCH=${BUILD_ARCH}

WORKDIR /usr/src

# Install elf
ARG PATCHELF_VERSION=0.11
RUN apk add --no-cache --virtual .build-dependencies \
        build-base \
        git \
        autoconf \
        automake \
    && git clone --depth 1 -b "${PATCHELF_VERSION}" https://github.com/NixOS/patchelf \
    && cd patchelf \
    && ./bootstrap.sh \
    && ./configure \
    && make "-j$(nproc)" \
    && make install \
    && apk del .build-dependencies \
    && rm -rf /usr/src/patchelf

# Install requirements
COPY requirements.txt /usr/src/
RUN apk add --no-cache \
        rsync \
        openssh-client \
    && pip3 install --no-cache-dir --find-links \
        "https://wheels.home-assistant.io/alpine-$(cut -d '.' -f 1-2 < /etc/alpine-release)/${BUILD_ARCH}/" \
        pip==20.2 \
    && pip3 install --no-cache-dir --find-links \
        "https://wheels.home-assistant.io/alpine-$(cut -d '.' -f 1-2 < /etc/alpine-release)/${BUILD_ARCH}/" \
        -r /usr/src/requirements.txt \
    && rm -f /usr/src/requirements.txt

# Install builder
COPY . /usr/src/builder/
RUN pip3 install --no-cache-dir \
        /usr/src/builder \
    && rm -fr /usr/src/builder

WORKDIR /data
ENTRYPOINT [ "python3", "-m", "builder" ]
