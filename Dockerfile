ARG BUILD_FROM
FROM ${BUILD_FROM}

ARG BUILD_ARCH
ENV ARCH=${BUILD_ARCH}

WORKDIR /usr/src

# Install requirements
COPY requirements.txt .
RUN apk add --no-cache \
        rsync \
        openssh-client \
        patchelf \
    && pip3 install --no-cache-dir --find-links \
        "https://wheels.home-assistant.io/alpine-$(cut -d '.' -f 1-2 < /etc/alpine-release)/${BUILD_ARCH}/" \
        -r requirements.txt \
    && rm -f requirements.txt

# Install builder
COPY . builder/
RUN pip3 install --no-cache-dir \
        builder/ \
    && rm -fr builder

WORKDIR /data
ENTRYPOINT [ "python3", "-m", "builder" ]
