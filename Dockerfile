ARG BUILD_FROM
FROM ${BUILD_FROM}

ARG BUILD_ARG
ENV ARCH=${BUILD_ARG}

# Install requirements
COPY requirements.txt /usr/src/
RUN apk add --no-cache \
    rsync \
    openssh-client \
    && apk add --no-cache --virtual .build-dependencies \
    make \
    g++ \
    openssl-dev \
    libffi-dev \
    musl-dev \
    && export MAKEFLAGS="-j$(nproc)" \
    && pip3 install --no-cache-dir -r /usr/src/requirements.txt \
    && apk del .build-dependencies \
    && rm -f /usr/src/requirements.txt

# Install builder
COPY . /usr/src/builder/
RUN apk add --no-cache /usr/src/builder \
    && rm -fr /usr/src/builder

WORKDIR /data
CMD [ "python3", "-m", "builder" ]
