# docker-gc

---

## Running

The container requires access to the docker socket in order to function, so you need to map it when running:

```shell
$ docker run --rm \
    -v /var/run/docker.sock:/var/run/docker.sock \
    r00m/docker-gc
```

## Building

```shell
$ docker build -t r00m/docker-gc:1.0.0 -t r00m/docker-gc .
```

## License

MIT