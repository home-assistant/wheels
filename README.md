# Home Assistant Wheels builder

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

`/alpine-{version}/{arch}/*`
