"""Deterministic, replayable simulation engine with fail-closed actions."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .contracts import (
    MAX_ACTIONS_PER_TICK,
    MAX_ENTITIES,
    MAX_EVENTS,
    MAX_TICKS_PER_STEP,
    ActionKind,
    WorldAction,
    WorldEntity,
    WorldEvent,
    WorldSnapshot,
    normalized_attributes,
    snapshot_digest,
)


@dataclass(frozen=True)
class SimulationResult:
    snapshot: WorldSnapshot
    events: tuple[WorldEvent, ...]
    accepted_actions: int
    rejected_actions: int


class SimulationWorld:
    """Small deterministic world model; it never executes arbitrary code."""

    def __init__(self, world_id: str, *, entities: Iterable[WorldEntity] = ()) -> None:
        if not isinstance(world_id, str) or not world_id.strip():
            raise ValueError("world_id is required")
        initial = tuple(entities)
        self._validate_entities(initial)
        self.world_id = world_id.strip()
        self.tick = 0
        self._entities = {e.entity_id: e for e in initial}
        self._events: list[WorldEvent] = []
        self._sequence = 0

    def snapshot(self) -> WorldSnapshot:
        entities = tuple(sorted(self._entities.values(), key=lambda e: e.entity_id))
        return WorldSnapshot(self.world_id, self.tick, entities, snapshot_digest(self.world_id, self.tick, entities))

    def events(self, *, limit: int = MAX_EVENTS) -> tuple[WorldEvent, ...]:
        if limit < 1 or limit > MAX_EVENTS:
            raise ValueError("event limit is out of bounds")
        return tuple(self._events[-limit:])

    def entity(self, entity_id: str) -> WorldEntity | None:
        return self._entities.get(entity_id)

    def add_entity(self, entity: WorldEntity) -> None:
        self._validate_entities(tuple(self._entities.values()) + (entity,))
        if entity.entity_id in self._entities:
            raise ValueError("entity_id already exists")
        self._entities[entity.entity_id] = entity

    def step(self, actions: Iterable[WorldAction] = (), *, ticks: int = 1) -> SimulationResult:
        if ticks < 1 or ticks > MAX_TICKS_PER_STEP:
            raise ValueError("tick count is out of bounds")
        pending = tuple(actions)
        if len(pending) > MAX_ACTIONS_PER_TICK:
            raise ValueError("action count is out of bounds")
        all_events: list[WorldEvent] = []
        accepted = rejected = 0
        for _ in range(ticks):
            for action in sorted(pending, key=lambda a: a.action_id):
                event = self._apply(action)
                all_events.append(event)
                accepted += int(event.accepted)
                rejected += int(not event.accepted)
            self.tick += 1
        return SimulationResult(self.snapshot(), tuple(all_events), accepted, rejected)

    def restore(self, snapshot: WorldSnapshot) -> None:
        if snapshot.world_id != self.world_id:
            raise ValueError("snapshot belongs to another world")
        self._validate_entities(snapshot.entities)
        if snapshot.digest != snapshot_digest(snapshot.world_id, snapshot.tick, snapshot.entities):
            raise ValueError("snapshot digest mismatch")
        self.tick = snapshot.tick
        self._entities = {e.entity_id: e for e in snapshot.entities}

    def _apply(self, action: WorldAction) -> WorldEvent:
        reason = "accepted"
        accepted = False
        if not action.action_id.strip() or not action.actor_id.strip():
            reason = "action identity is required"
        elif action.actor_id not in self._entities:
            reason = "actor does not exist"
        elif action.kind is ActionKind.MOVE:
            accepted, reason = self._move(action)
        elif action.kind is ActionKind.SET:
            accepted, reason = self._set_attribute(action)
        elif action.kind is ActionKind.TRANSFER:
            accepted, reason = self._transfer_energy(action)
        elif action.kind is ActionKind.REMOVE:
            accepted, reason = self._remove(action)
        else:
            reason = "unsupported action"
        self._sequence += 1
        return WorldEvent(self.tick, self._sequence, action.action_id, action.actor_id, action.kind.value, action.target_id, accepted, reason, self.snapshot().digest)

    def _move(self, action: WorldAction) -> tuple[bool, str]:
        if action.target_id not in self._entities:
            return False, "target does not exist"
        try:
            dx, dy = (int(part) for part in action.value.split(",", 1))
        except (TypeError, ValueError):
            return False, "move value must be 'dx,dy'"
        if abs(dx) > 16 or abs(dy) > 16:
            return False, "movement exceeds bounded step"
        actor = self._entities[action.actor_id]
        self._entities[action.actor_id] = WorldEntity(actor.entity_id, actor.kind, actor.x + dx, actor.y + dy, max(0, actor.energy - 1), actor.attributes)
        return True, "moved"

    def _set_attribute(self, action: WorldAction) -> tuple[bool, str]:
        if action.target_id not in self._entities:
            return False, "target does not exist"
        if not action.value or "=" not in action.value:
            return False, "set value must be key=value"
        key, value = action.value.split("=", 1)
        key, value = key.strip(), value.strip()
        if not key or len(key) > 64 or len(value) > 256:
            return False, "attribute is out of bounds"
        entity = self._entities[action.target_id]
        attrs = dict(entity.attributes)
        attrs[key] = value
        self._entities[action.target_id] = WorldEntity(entity.entity_id, entity.kind, entity.x, entity.y, entity.energy, normalized_attributes(attrs))
        return True, "attribute updated"

    def _transfer_energy(self, action: WorldAction) -> tuple[bool, str]:
        if action.target_id not in self._entities:
            return False, "target does not exist"
        try:
            amount = int(action.value)
        except (TypeError, ValueError):
            return False, "transfer amount must be an integer"
        if amount <= 0 or amount > 50:
            return False, "transfer amount is out of bounds"
        actor, target = self._entities[action.actor_id], self._entities[action.target_id]
        if actor.energy < amount:
            return False, "insufficient energy"
        self._entities[action.actor_id] = WorldEntity(actor.entity_id, actor.kind, actor.x, actor.y, actor.energy - amount, actor.attributes)
        self._entities[action.target_id] = WorldEntity(target.entity_id, target.kind, target.x, target.y, min(100, target.energy + amount), target.attributes)
        return True, "energy transferred"

    def _remove(self, action: WorldAction) -> tuple[bool, str]:
        if action.target_id not in self._entities:
            return False, "target does not exist"
        if action.target_id == action.actor_id:
            return False, "actor cannot remove itself"
        del self._entities[action.target_id]
        return True, "entity removed"

    @staticmethod
    def _validate_entities(entities: tuple[WorldEntity, ...]) -> None:
        if len(entities) > MAX_ENTITIES:
            raise ValueError("entity count is out of bounds")
        ids = [e.entity_id for e in entities]
        if any(not isinstance(e.entity_id, str) or not e.entity_id.strip() for e in entities):
            raise ValueError("entity_id is required")
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate entity_id")
        if any(e.energy < 0 or e.energy > 100 for e in entities):
            raise ValueError("energy is out of bounds")
