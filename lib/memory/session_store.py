import copy
from abc import ABC, abstractmethod
from typing import Any


class SessionStore(ABC):
    """Abstract interface for persisting agent conversation state.

    Swap the in-memory implementation for a DB-backed one later without
    touching any calling code.
    """

    @abstractmethod
    async def load(self, session_id: str) -> list[dict[str, Any]]:
        """Return the full steps_history for a session, or [] if none exists."""
        ...

    @abstractmethod
    async def save(self, session_id: str, steps_history: list[dict[str, Any]]) -> None:
        """Overwrite the full steps_history for a session."""
        ...

    @abstractmethod
    async def append(self, session_id: str, step: dict[str, Any]) -> None:
        """Append a single step. Preferred over save() for per-step checkpointing."""
        ...


class InMemorySessionStore(SessionStore):
    """Simple dict-backed store. Data is lost when the process exits.
    Swap for a DB-backed SessionStore later; interface stays the same.
    """

    def __init__(self) -> None:
        self._sessions: dict[str, list[dict[str, Any]]] = {}

    async def load(self, session_id: str) -> list[dict[str, Any]]:
        return copy.deepcopy(self._sessions.get(session_id, []))

    async def save(self, session_id: str, steps_history: list[dict[str, Any]]) -> None:
        self._sessions[session_id] = copy.deepcopy(steps_history)

    async def append(self, session_id: str, step: dict[str, Any]) -> None:
        self._sessions.setdefault(session_id, []).append(copy.deepcopy(step))