"""Adapters connecting simulation to the existing DORMAMMU control plane."""
from __future__ import annotations

from dataclasses import dataclass
from time import monotonic
from typing import Any, Iterable

from .contracts import WorldAction, WorldEntity
from .engine import SimulationResult, SimulationWorld
from .persistence import SimulationStore


@dataclass(frozen=True)
class SimulationRun:
    result: SimulationResult
    reservation_id: str | None
    resource_id: str | None


class SimulationRuntimeAdapter:
    """Host-controlled simulation facade; world actions remain scoped to the world model."""

    def __init__(self, runtime: Any, *, store_path: str = ":memory:") -> None:
        self.runtime = runtime
        self.store = SimulationStore(store_path)
        self._worlds: dict[str, SimulationWorld] = {}

    def create_world(self, world_id: str, *, entities: Iterable[WorldEntity] = ()) -> SimulationWorld:
        if world_id in self._worlds:
            raise ValueError("world_id already exists")
        world = SimulationWorld(world_id, entities=entities)
        self._worlds[world_id] = world
        self.store.save(world.snapshot())
        return world

    def world(self, world_id: str) -> SimulationWorld | None:
        return self._worlds.get(world_id)

    def step(self, world_id: str, actions: Iterable[WorldAction] = (), *, ticks: int = 1, resource_id: str | None = None, resource_quantity: float | None = None) -> SimulationRun:
        world = self._worlds.get(world_id)
        if world is None:
            raise KeyError(world_id)
        start = monotonic()
        reservation_id = None
        if resource_id is not None:
            if resource_quantity is None or resource_quantity <= 0:
                raise ValueError("resource_quantity is required for resource-backed simulation")
            # Reuse the existing resource decision path; simulation never provisions resources.
            from ...capabilities import ResourceRequest
            decision = self.runtime.decide_resource(ResourceRequest(resource_id, resource_quantity, "simulation", world_id))
            if not decision.allowed:
                raise RuntimeError("simulation resource request denied")
            reservation_id = self.runtime.reserve_resource(ResourceRequest(resource_id, resource_quantity, "simulation", world_id)).reservation_id
        result = world.step(actions, ticks=ticks)
        self.store.save(result.snapshot)
        self.runtime.record_operation_observation_from_result(
            "simulation:" + world_id + ":" + str(result.snapshot.tick),
            "simulation.world",
            "simulate",
            True,
            all(e.accepted or e.reason for e in result.events),
            (monotonic() - start) * 1000,
            "bounded deterministic simulation step",
            resource_id,
            resource_quantity,
        )
        return SimulationRun(result, reservation_id, resource_id)

    def recover_latest(self, world_id: str) -> SimulationWorld:
        snapshot = self.store.load(world_id)
        if snapshot is None:
            raise KeyError(world_id)
        world = self._worlds.get(world_id) or SimulationWorld(world_id)
        world.restore(snapshot)
        self._worlds[world_id] = world
        return world

    def close(self) -> None:
        self.store.close()
