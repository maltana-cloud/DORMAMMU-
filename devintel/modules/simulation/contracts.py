"""Stable contracts for bounded deterministic simulation worlds."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
from typing import Mapping

MAX_ENTITIES = 256
MAX_ACTIONS_PER_TICK = 128
MAX_EVENTS = 4096
MAX_TICKS_PER_STEP = 64


class EntityKind(str, Enum):
    ACTOR = "actor"
    OBJECT = "object"
    LOCATION = "location"


class ActionKind(str, Enum):
    MOVE = "move"
    SET = "set"
    TRANSFER = "transfer"
    REMOVE = "remove"


@dataclass(frozen=True)
class WorldEntity:
    entity_id: str
    kind: EntityKind
    x: int = 0
    y: int = 0
    energy: int = 100
    attributes: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class WorldAction:
    action_id: str
    actor_id: str
    kind: ActionKind
    target_id: str = ""
    value: str = ""


@dataclass(frozen=True)
class WorldEvent:
    tick: int
    sequence: int
    action_id: str
    actor_id: str
    kind: str
    target_id: str
    accepted: bool
    reason: str
    state_digest: str


@dataclass(frozen=True)
class WorldSnapshot:
    world_id: str
    tick: int
    entities: tuple[WorldEntity, ...]
    digest: str


def canonical_entity(entity: WorldEntity) -> str:
    attrs = ";".join(f"{k}={v}" for k, v in sorted(entity.attributes))
    return f"{entity.entity_id}|{entity.kind.value}|{entity.x}|{entity.y}|{entity.energy}|{attrs}"


def snapshot_digest(world_id: str, tick: int, entities: tuple[WorldEntity, ...]) -> str:
    payload = "\n".join([world_id, str(tick), *(canonical_entity(e) for e in sorted(entities, key=lambda e: e.entity_id))])
    return sha256(payload.encode()).hexdigest()


def normalized_attributes(values: Mapping[str, object]) -> tuple[tuple[str, str], ...]:
    return tuple(sorted((str(k), str(v)) for k, v in values.items()))
