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
    resources: list[ResourceDescriptor] = [ResourceDescriptor(
        "host:cpu", ResourceKind.CPU, platform.processor() or platform.machine(),
        capacity=str(os.cpu_count() or 1), availability="ready", permissions=("approved",),
        metadata={"logical_cores": str(os.cpu_count() or 1), "architecture": platform.machine(), "allocatable": str(os.cpu_count() or 1)},
    )]
    memory = _memory_bytes()
    resources.append(ResourceDescriptor(
        "host:ram", ResourceKind.RAM, "system memory", capacity=str(memory or 0),
        availability="ready" if memory else "unknown", permissions=("approved",), metadata={"bytes": str(memory or 0), "allocatable": str(memory or 0)},
    ))
    try:
        disk = shutil.disk_usage(os.getcwd())
        resources.append(ResourceDescriptor(
            "host:storage", ResourceKind.STORAGE, "working filesystem", capacity=str(disk.total),
            availability="ready", permissions=("approved",), metadata={"free_bytes": str(disk.free), "used_bytes": str(disk.used), "allocatable": str(disk.free)},
        ))
    except OSError:
        pass
    gpu = os.environ.get("DORMAMMU_GPU") or os.environ.get("CUDA_VISIBLE_DEVICES")
    if gpu and gpu not in {"", "-1"}:
        resources.append(ResourceDescriptor("host:gpu", ResourceKind.GPU, gpu, availability="declared", permissions=("approved",), metadata={"source": "environment"}))
    return tuple(resources)


def local_capabilities() -> tuple[CapabilityDescriptor, ...]:
    return (
        CapabilityDescriptor(
            "runtime.local", "Local DORMAMMU runtime", "1.0", ("runtime",), "dormammu",
            "internal", status=CapabilityStatus.ACTIVE, permissions=("approved",),
            metadata={"platform": platform.system(), "python": platform.python_version()},
        ),
    )
