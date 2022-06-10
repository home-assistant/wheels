# Home Assistant Musl Wheels builder

https://peps.python.org/pep-0656/

## Platform tags

### Python 3.10 / musllinux_1_2

Build with Alpine 3.16
Images: ghcr.io/home-assistant/wheels/musllinux_1_2/python3.10

Version of system builds:

- Numpy 1.22

## Misc

```sh

$ python3 -m builder \
    --apk build-base \
    --index https://wheels.home-assistant.io \
    --requirement requirements_all.txt \
    --upload rsync \
    --remote user@server:/wheels
```

## Supported file transfer

- rsync

## Folder structure of index folder:

`/musllinux/*`
