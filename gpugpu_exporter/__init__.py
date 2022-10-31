import sys
import time
from typing import Any, Dict, Iterable, List

from loguru import logger
from prometheus_client import Gauge, start_http_server
from tenacity import retry, stop_after_attempt, wait_exponential

from gpugpu_exporter.gpus import GPU, all_gpus
from gpugpu_exporter.utils import find_container_by_pid

logger.remove()
logger.add(
    sys.stderr,
    colorize=True,
    format=(
        "<green><bold>[{time:YYYY-MM-DD HH:mm:ss.SSS}]</bold></green>"
        " <level>[{level}]</level> {message}"
    ),
)

def get_friendly_name_of_process(process: GPU.Process) -> str:
    container = find_container_by_pid(process.pid)
    if container:
        return container.name
    else:
        return process.user


class GPUGPUExporter:
    def __init__(self, port: int, interval: float):
        self.port = port
        self.interval = interval

        self.initialize_metrics()

    def start_server(self):
        logger.info(f"Starting http server on {self.port}")
        start_http_server(self.port)
        self.run_metrics_loop()

    @retry(wait=wait_exponential(multiplier=1, min=2, max=60), stop=stop_after_attempt(10))
    def run_metrics_loop(self):
        while True:
            metrics = list(self.gather_metrics())
            self.update_metrics(metrics)

            logger.info(f"Sleeping {self.interval}s...")
            time.sleep(self.interval)

    def initialize_metrics(self):
        self.gpu_memory_used = Gauge(
            name="gpu_memory_used",
            documentation="GPU memory used by a user or a container",
            labelnames=[
                "gpu_id",
                "user",
            ],
        )

    def gather_metrics(self) -> Iterable[Dict[str, Any]]:
        with all_gpus() as gpus:
            for gpu in gpus:
                for process in gpu.processes:
                    yield {
                        "gpu_id": gpu.id,
                        "user": get_friendly_name_of_process(process),
                        "memory_used": process.used_memory,
                    }

    def update_metrics(self, metrics: List[Dict[str, Any]]):
        logger.info("Updating metrics...")

        self.gpu_memory_used.clear()
        for metric in metrics:
            self.gpu_memory_used.labels(
                gpu_id=metric["gpu_id"], user=metric["user"]
            ).set(metric["memory_used"])
