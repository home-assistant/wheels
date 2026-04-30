# Home Assistant Musl Wheels builder

https://peps.python.org/pep-0656/

## Platform tags

Compile utilities:

- build-base
- cmake
- git
- linux-headers
- autoconf
- automake
- cargo

### Python 3.13 / musllinux_1_2

Build with Alpine 3.23
Images: ghcr.io/home-assistant/wheels/ARCH/musllinux_1_2/cp313:VERSION

Version of system builds:

- GCC 15.2.0
- rust 1.91.1
- Cython 3.2.4
- numpy 2.4.4
- scikit-build 0.19.0
- cffi 2.0.0

### Python 3.14 / musllinux_1_2

Build with Alpine 3.23
Images: ghcr.io/home-assistant/wheels/ARCH/musllinux_1_2/cp314:VERSION

Version of system builds:

- GCC 15.2.0
- rust 1.91.1
- Cython 3.2.4
- numpy 2.4.4
- scikit-build 0.19.0
- cffi 2.0.0

## Misc

```sh

$ python3 -m builder \
    --index https://wheels.home-assistant.io \
    --requirement requirements_all.txt \
    --upload rsync \
    --remote user@server:/wheels
```

## Supported file transfer

- rsync

## Folder structure of index folder:

`/musllinux/*`
