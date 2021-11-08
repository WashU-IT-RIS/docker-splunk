#!/usr/bin/env bash
set -exau

docker tag "${bamboo_ris_container_target}:latest" \
           "${bamboo_ris_container_repo_path}:${bamboo_repository_branch_name}"
docker tag "${bamboo_ris_container_target}:latest" \
           "${bamboo_ris_container_repo_path}:bamboo-build-${bamboo_buildNumber}"
if [ "$bamboo_repository_branch_name" == "$bamboo_ris_prod_branch" ] ; then
    docker tag "${bamboo_ris_container_target}:latest" \
               "${bamboo_ris_container_repo_path}:latest"
    docker tag "${bamboo_ris_container_target}:latest" \
               "${bamboo_ris_container_repo_path}:production"
    docker tag "${bamboo_ris_container_target}:latest" \
               "${bamboo_ris_container_repo_path}:${bamboo_ris_splunk_version}"
fi
