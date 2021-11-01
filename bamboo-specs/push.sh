#!/usr/bin/env bash
set -exau

if [ "$bamboo_repository_branch_name" == "$bamboo_ris_prod_branch" ] ; then
    docker push "${bamboo_ris_container_repo_path}:latest"
    docker push "${bamboo_ris_container_repo_path}:production"
    docker push "${bamboo_ris_container_repo_path}:${bamboo_ris_splunk_version}"
fi
docker push "${bamboo_ris_container_repo_path}:${bamboo_repository_branch_name}"
docker push "${bamboo_ris_container_repo_path}:bamboo-build-${bamboo_buildNumber}"
