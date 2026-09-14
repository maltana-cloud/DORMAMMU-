"""Thread-safe registries for capabilities, gaps, and compute/resources."""
from __future__ import annotations

from threading import RLock
from .contracts import CapabilityDescriptor, CapabilityGap, ResourceDescriptor


class CapabilityRegistry:
    def __init__(self, max_items: int = 512, store: CapabilityRegistryStore | None = None) -> None:
        if max_items <= 0: raise ValueError("max_items must be positive")
        self._max = max_items; self._items: dict[str, CapabilityDescriptor] = {}; self._lock = RLock(); self._store = store
        if store:
            for item in store.load_all():
                if len(self._items) >= self._max: break
                self._items[item.capability_id] = item

    def register(self, item: CapabilityDescriptor) -> None:
        with self._lock:
            if item.capability_id not in self._items and len(self._items) >= self._max: raise RuntimeError("capability registry capacity reached")
            self._items[item.capability_id] = item
            if self._store: self._store.save(item)

    def get(self, capability_id: str) -> CapabilityDescriptor | None:
        with self._lock: return self._items.get(capability_id)

    def ids(self) -> tuple[str, ...]:
        with self._lock: return tuple(sorted(self._items))


class GapRegistry:
    def __init__(self, max_items: int = 512) -> None:
        if max_items <= 0: raise ValueError("max_items must be positive")
        self._max = max_items; self._items: dict[str, CapabilityGap] = {}; self._lock = RLock()

    def record(self, gap: CapabilityGap) -> None:
        with self._lock:
            if gap.gap_id not in self._items and len(self._items) >= self._max: raise RuntimeError("gap registry capacity reached")
            self._items[gap.gap_id] = gap

    def get(self, gap_id: str) -> CapabilityGap | None:
        with self._lock: return self._items.get(gap_id)

    def all(self) -> tuple[CapabilityGap, ...]:
        with self._lock: return tuple(self._items.values())


class ResourceRegistry:
    def __init__(self, max_items: int = 512) -> None:
        if max_items <= 0: raise ValueError("max_items must be positive")
        self._max = max_items; self._items: dict[str, ResourceDescriptor] = {}; self._lock = RLock()

    def register(self, item: ResourceDescriptor) -> None:
        with self._lock:
            if item.resource_id not in self._items and len(self._items) >= self._max: raise RuntimeError("resource registry capacity reached")
            self._items[item.resource_id] = item

    def get(self, resource_id: str) -> ResourceDescriptor | None:
        with self._lock: return self._items.get(resource_id)

    def all(self) -> tuple[ResourceDescriptor, ...]:
        with self._lock: return tuple(self._items.values())
