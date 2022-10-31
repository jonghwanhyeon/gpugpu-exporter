from __future__ import annotations

from contextlib import contextmanager
from typing import ContextManager, List, NamedTuple

import psutil
from pynvml import *


class GPU:
    class Memory(NamedTuple):
        total: int
        used: int
        free: int

    class Power(NamedTuple):
        usage: float
        limit: float

    class Process(NamedTuple):
        pid: int
        user: str
        name: str
        used_memory: int

    def __init__(self, id: int):
        self.id = id
        self.handle = nvmlDeviceGetHandleByIndex(id)

    @property
    def name(self) -> str:
        return nvmlDeviceGetName(self.handle).decode()

    @property
    def memory(self) -> GPU.Memory:
        m = nvmlDeviceGetMemoryInfo(self.handle)
        return GPU.Memory(total=m.total, used=m.used, free=m.free)

    @property
    def utilization(self) -> int:
        return nvmlDeviceGetUtilizationRates(self.handle).gpu

    @property
    def temperature(self) -> int:
        return nvmlDeviceGetTemperature(self.handle, NVML_TEMPERATURE_GPU)

    @property
    def power(self) -> GPU.Power:
        return GPU.Power(
            usage=nvmlDeviceGetPowerUsage(self.handle) / 1000,
            limit=nvmlDeviceGetPowerManagementLimit(self.handle) / 1000,
        )

    @property
    def processes(self) -> GPU.Process:
        for p in nvmlDeviceGetComputeRunningProcesses(self.handle):
            try:
                name = nvmlSystemGetProcessName(p.pid).decode()
            except NVMLError:
                name = None

            yield GPU.Process(
                pid=p.pid,
                user=psutil.Process(p.pid).username(),
                name=name,
                used_memory=p.usedGpuMemory,
            )


@contextmanager
def all_gpus() -> ContextManager[List[GPU]]:
    nvmlInit()
    yield [GPU(id) for id in range(nvmlDeviceGetCount())]
    nvmlShutdown()
