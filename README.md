# Splunk Docker Container

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)&nbsp;
[![GitHub release](https://img.shields.io/github/v/tag/splunk/docker-splunk?sort=semver&label=Version)](https://github.com/splunk/docker-splunk/releases)

## Remotes

This is a clone of Splunk's own container build sources:

```
$ git remote -v
risgh	git@github.com:WashU-IT-RIS/docker-splunk.git (fetch)
risgh	git@github.com:WashU-IT-RIS/docker-splunk.git (push)
upstream	git@github.com:splunk/docker-splunk.git (fetch)
upstream	git@github.com:splunk/docker-splunk.git (push)
```

It is rehosted (GitHub-forked) here to allow us to augment it and reduce external dependency.

## Versions

Chose the latest version to build:

```
$ git tag -l | sort -V | tail -n1
9.2.1
```
