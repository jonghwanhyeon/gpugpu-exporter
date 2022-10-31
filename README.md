# gpugpu-exporter
Prometheus Exporter for GPU memory usage metrics of docker containers

## Usage
To run it:

```bash
$ docker run \
    --detach \
    --restart=always \
    --gpus=all \
    --pid=host \
    --volume /var/run/docker.sock:/tmp/docker.sock:ro \
    --publish=9700:9700 \
    --name=prometheus-gpugpu-exporter \
    ghcr.io/jonghwanhyeon/gpugpu-exporter
```