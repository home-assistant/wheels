#!/usr/bin/env bashio
declare RUN_CMD="python3 -m builder"

# Ensure that we show 32bit at an 64bit CI
if [ "${ARCH}" = "i386" ] && [ "$(uname -m)" = "x86_64" ]; then
    bashio::log.info "Use linux32 for CPU mask"
    RUN_CMD="linux32 ${RUN_CMD}"
fi

# Ensure that armv6 is masked on Qemu
if [ "${ARCH}" = "armhf" ] && [ "$(uname -m)" = "armv7l" ]; then
    bashio::log.info "Use QEMU_CPU for CPU mask"
    export QEMU_CPU=arm1176
fi

# shellcheck disable=SC2068
exec ${RUN_CMD} $@
