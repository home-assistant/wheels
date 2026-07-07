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

### Python 3.14 / musllinux_1_2

Build with Alpine 3.24
Images: ghcr.io/home-assistant/wheels/ARCH/musllinux_1_2/cp314:VERSION

Version of system builds can be found by checking:

- [requirements_cp314.txt](requirements_cp314.txt)
- https://pkgs.alpinelinux.org/packages?branch=v3.24

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

## Uploading over Tailscale

The [wheels-server](https://github.com/home-assistant/wheels-server) is not
publicly reachable — it accepts rsync uploads only over a Tailscale tailnet.
The `tailscale-oauth-client-id` and `tailscale-oauth-secret` inputs are
therefore required: the runner joins the tailnet as an ephemeral node (tagged
`tag:homeassistant-wheels-deploy-action` by default, override with
`tailscale-tags`) before uploading to `wheels-host`:

```yaml
- name: Build wheels
  uses: home-assistant/wheels@2026.07.0
  with:
    abi: cp314
    tag: musllinux_1_2
    arch: amd64
    wheels-key: ${{ secrets.WHEELS_KEY }}
    wheels-host: wheels.<your-tailnet>.ts.net
    tailscale-oauth-client-id: ${{ secrets.TS_OAUTH_CLIENT_ID }}
    tailscale-oauth-secret: ${{ secrets.TS_OAUTH_SECRET }}
    requirements: "requirements.txt"
```

In test mode (`test: true`) and when publishing to a local folder
(`local-wheels-repo-path`), nothing is uploaded and the runner does not join
the tailnet. To publish to two servers during a migration, run the action
twice (one step per host).

## Folder structure of index folder:

`/musllinux/*`
