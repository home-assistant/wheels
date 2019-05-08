ARG BUILD_FROM
FROM ${BUILD_FROM}

ARG BUILD_ARCH
ENV ARCH=${BUILD_ARCH}

# Install requirements
COPY requirements.txt /usr/src/
RUN apk add --no-cache \
        rsync \
        openssh-client \
    && pip3 install --no-cache-dir --find-links https://wheels.hass.io/alpine-3.9/${BUILD_ARCH}/ \
        -r /usr/src/requirements.txt \
    && rm -f /usr/src/requirements.txt

# Install builder
COPY . /usr/src/builder/
RUN pip3 install --no-cache-dir \
        /usr/src/builder \
    && rm -fr /usr/src/builder

WORKDIR /data
ENTRYPOINT [ "python3", "-m", "builder" ]
