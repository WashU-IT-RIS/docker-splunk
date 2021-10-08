# Splunk Docker Container

## Remotes

This is a clone of Splunk's own container build sources:

```
$ git remote -v
origin  git@github.com:splunk/docker-splunk.git (fetch)
origin  git@github.com:splunk/docker-splunk.git (push)
ris     ssh://git@bitbucket.wustl.edu:2222/rdi/splunk.git (fetch)
ris     ssh://git@bitbucket.wustl.edu:2222/rdi/splunk.git (push)
```

It is rehosted here to remove external dependencies and so it can be
build by `bamboo.wustl.edu` and pushed to a local container repository.

## Versions

Chose the latest version to build:

```
$ git tag -l | sort -V | tail -n1
8.2.1
```
