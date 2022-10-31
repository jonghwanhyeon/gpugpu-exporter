from itertools import chain
from typing import Optional, Set

import docker
from docker.models.containers import Container

docker_client = docker.DockerClient(base_url="unix://tmp/docker.sock")


def get_pids(container: Container) -> Set[int]:
    return set(
        map(int, chain.from_iterable(container.top(ps_args="-o pid")["Processes"]))
    )


def find_container_by_pid(pid: int) -> Optional[Container]:
    for container in docker_client.containers.list():
        if pid in get_pids(container):
            return container
    return None
