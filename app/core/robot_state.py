from typing import Dict, Any, List
import asyncio
from pydantic import BaseModel

class RobotStateModel(BaseModel):
    manufacturer: str
    serial_number: str
    last_message_type: str = ""
    payload: Dict[str, Any] = {}

class RobotState:
    """In-memory store + pub-sub for robot state updates.
    Use RobotState.get_instance() to access the singleton.
    """
    _instance = None

    def __init__(self):
        self._states: Dict[str, RobotStateModel] = {}
        self._subs: List[asyncio.Queue] = []
        self._lock = asyncio.Lock()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = RobotState()
        return cls._instance

    async def update_from_mqtt(self, manufacturer: str, serial: str, msg_type: str, payload: Dict[str, Any]):
        key = f"{manufacturer}/{serial}"
        model = RobotStateModel(
            manufacturer=manufacturer,
            serial_number=serial,
            last_message_type=msg_type,
            payload=payload,
        )
        async with self._lock:
            self._states[key] = model
            # publish to subscribers (non-blocking)
            data = {"topic": key, "type": msg_type, "payload": payload}
            for q in list(self._subs):
                # put_nowait so slow clients don't block; if full, drop oldest
                try:
                    q.put_nowait(data)
                except asyncio.QueueFull:
                    # make space then put
                    try:
                        _ = q.get_nowait()
                    except Exception:
                        pass
                    try:
                        q.put_nowait(data)
                    except Exception:
                        pass

    async def get_snapshot(self) -> Dict[str, Any]:
        async with self._lock:
            return {k: v.dict() for k, v in self._states.items()}

    async def subscribe(self, max_queue=100) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue(maxsize=max_queue)
        async with self._lock:
            self._subs.append(q)
        return q

    async def unsubscribe(self, q: asyncio.Queue):
        async with self._lock:
            try:
                self._subs.remove(q)
            except ValueError:
                pass
