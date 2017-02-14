# docker-marathon-acme

[![Requirements Status](https://requires.io/github/praekeltfoundation/docker-marathon-acme/requirements.svg?branch=master)](https://requires.io/github/praekeltfoundation/docker-marathon-acme/requirements/?branch=master)
[![Build Status](https://travis-ci.org/praekeltfoundation/docker-marathon-acme.svg?branch=master)](https://travis-ci.org/praekeltfoundation/docker-marathon-acme)

Release Docker images for [`marathon-acme`](https://github.com/praekeltfoundation/marathon-acme).

## Usage
Arguments can be provided to the container to configure `marathon-acme`:
```
> $ docker run --rm praekeltfoundation/marathon-acme --help
usage: marathon-acme [-h] [-a ACME] [-e EMAIL] [-m MARATHON[,MARATHON,...]]
                     [-l LB[,LB,...]] [-g GROUP] [--listen LISTEN]
                     [--log-level {debug,info,warn,error,critical}]
                     storage-dir

Automatically manage ACME certificates for Marathon apps

...
```

By default, this Docker image stores certificates to `/var/lib/marathon-acme` which is advertised as a volume. It exposes port `8000`.

In most cases, `marathon-acme` should be run using Marathon itself. Here is an example of an app definition:
```json
{
  "id": "/marathon-acme",
  "cpus": 0.01,
  "mem": 128.0,
  "args": [
    "--email", "letsencrypt@example.com",
    "--marathon", "http://marathon1:8080,http://marathon2:8080,http://marathon3:8080",
    "--lb", "http://lb1:9090,http://lb2:9090",
    "/var/lib/marathon-acme"
  ],
  "labels": {
    "HAPROXY_GROUP": "external",
    "HAPROXY_0_VHOST": "example.com",
    "HAPROXY_0_BACKEND_WEIGHT": "1",
    "HAPROXY_0_PATH": "/.well-known/acme-challenge/",
    "HAPROXY_0_HTTP_FRONTEND_ACL_WITH_PATH": "  acl path_{backend} path_beg {path}\n  use_backend {backend} if path_{backend}\n",
    "HAPROXY_0_HTTPS_FRONTEND_ACL_WITH_PATH": "  use_backend {backend} if path_{backend}\n"
  },
  "container": {
    "type": "DOCKER",
    "docker": {
      "image": "praekeltfoundation/marathon-acme",
      "network": "BRIDGE",
      "portMappings": [
        { "containerPort": 8000, "hostPort": 0 }
      ],
      "parameters": [
        {
          "value": "my-volume-driver",
          "key": "volume-driver"
        },
        {
          "value": "marathon-acme-certs:/var/lib/marathon-acme",
          "key": "volume"
        }
      ],
    }
  }
}
```

Please see the [`marathon-acme` repository](https://github.com/praekeltfoundation/marathon-acme) for more information about configuration.

### Runtime user
By default, `marathon-acme` will run as `root` inside its container. Because `marathon-acme` will usually be set up to store certificates in a networked storage volume, filesystem permissions would get complicated if we were to create and use a lesser-privileged user inside the container.

However, a user can be specified to switch to when running `marathon-acme`, using the `MARATHON_ACME_USER` environment variable. It is up to you to make sure that user will have the correct filesystem permissions within whatever networked storage you use.

The value of the `MARATHON_ACME_USER` variable is of the same format as that provided to the [`USER` Dockerfile directive](https://docs.docker.com/engine/reference/builder/#/user). You could either switch to an explicit, known-good UID/GID (without the user necessarily existing) or create a new image based on this one that creates the user/group that you want.
