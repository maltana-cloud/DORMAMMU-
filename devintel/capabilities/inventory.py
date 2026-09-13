"""Safe, read-only local capability and resource inventory."""
from __future__ import annotations
import os
import platform
import shutil
from .contracts import CapabilityDescriptor, CapabilityStatus, ResourceDescriptor, ResourceKind


def _memory_bytes() -> int | None:
    try:
        with open("/proc/meminfo", encoding="utf-8") as handle:
            for line in handle:
                if line.startswith("MemTotal:"):
                    return int(line.split()[1]) * 1024
    except (OSError, ValueError, IndexError):
        return None
    return None


def local_resources() -> tuple[ResourceDescriptor, ...]:
    resources: list[ResourceDescriptor] = []
    resources.append(ResourceDescriptor(
        "host:cpu", ResourceKind.CPU, platform.processor() or platform.machine(),
        capacity=str(os.cpu_count() or 1), availability="ready",
        metadata={"logical_cores": str(os.cpu_count() or 1), "architecture": platform.machine()},
    ))
    memory = _memory_bytes()
    resources.append(ResourceDescriptor(
        "host:ram", ResourceKind.OTHER, "system memory", capacity=str(memory or 0),
        availability="ready" if memory else "unknown", metadata={"bytes": str(memory or 0)},
    ))
    try:
        disk = shutil.disk_usage(os.getcwd())
        resources.append(ResourceDescriptor(
            "host:storage", ResourceKind.STORAGE, "working filesystem", capacity=str(disk.total),
            availability="ready", metadata={"free_bytes": str(disk.free), "used_bytes": str(disk.used)},
        ))
    except OSError:
        pass
    gpu = os.environ.get("DORMAMMU_GPU") or os.environ.get("CUDA_VISIBLE_DEVICES")
    if gpu and gpu not in {"", "-1"}:
        resources.append(ResourceDescriptor("host:gpu", ResourceKind.GPU, gpu, availability="declared", metadata={"source": "environment"}))
    return tuple(resources)


def local_capabilities() -> tuple[CapabilityDescriptor, ...]:
    return (
        CapabilityDescriptor(
            "runtime.local", "Local DORMAMMU runtime", "1.0", ("runtime",), "dormammu",
            "internal", status=CapabilityStatus.ACTIVE, permissions=("approved",),
            metadata={"platform": platform.system(), "python": platform.python_version()},
        ),
    )
