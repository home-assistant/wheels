[![Build Status](https://dev.azure.com/home-assistant/Hass.io/_apis/build/status/wheels?branchName=master)](https://dev.azure.com/home-assistant/Hass.io/_build/latest?definitionId=11&branchName=master)

# Hass.io Wheels builder

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
