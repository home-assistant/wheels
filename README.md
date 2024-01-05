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

### Python 3.12 / musllinux_1_2

Build with Alpine 3.19
Images: ghcr.io/home-assistant/wheels/ARCH/musllinux_1_2/cp312:VERSION

Version of system builds:

- GCC 12.2.1
- Cython 3.0.7
- numpy 1.26.0
- scikit-build 0.17.1
- cffi 1.16.0


### Python 3.11 / musllinux_1_2

Build with Alpine 3.19
Images: ghcr.io/home-assistant/wheels/ARCH/musllinux_1_2/cp311:VERSION

Version of system builds:

- GCC 12.2.1
- Cython 3.0.7
- numpy 1.26.3
- scikit-build 0.17.1
- cffi 1.16.0

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
