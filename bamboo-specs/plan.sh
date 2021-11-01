#!/usr/bin/env bash
set -exau

cleanup() {
    RC="$?"
    trap - ERR QUIT TERM EXIT INT KILL
    rm "${DOCKER_CONFIG}/config.json" || echo "warning: error deleting docker secret config file" >&2
    rmdir "${AUTH_TEMPDIR}" || echo "warning: error deleting auth secret temp dir" >&2
    exit "$RC"
}

if [ ! -f "debug_auth" ]; then
    trap cleanup ERR QUIT TERM EXIT INT KILL
fi

umask 0077
export AUTH_TEMPDIR="$(mktemp -d -p . .build_temp_XXXXX)"

export DOCKER_CONFIG="$AUTH_TEMPDIR"
cat > "${DOCKER_CONFIG}/config.json" <<<"${bamboo_docker_config_secret:-$(pass registry.gsc.wustl.edu/genome/config.json)}"

bamboo-specs/build.sh
bamboo-specs/tag.sh
bamboo-specs/push.sh
