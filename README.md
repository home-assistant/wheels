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

Build with Alpine 3.22
Images: ghcr.io/home-assistant/wheels/ARCH/musllinux_1_2/cp313:VERSION

Version of system builds:

- GCC 13.2.1
- Cython 3.0.12
- numpy 2.2.2
- scikit-build 0.18.1
- cffi 1.17.1


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
