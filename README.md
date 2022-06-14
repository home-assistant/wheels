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

### Python 3.10 / musllinux_1_2

Build with Alpine 3.16
Images: ghcr.io/home-assistant/wheels/ARCH/musllinux_1_2/cp310:VERSION

Version of system builds:

- GCC 11.2.1
- Cython 0.29.30
- numpy 1.22.4
- scikit-build 0.15.0
- cffi 1.15.0

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
