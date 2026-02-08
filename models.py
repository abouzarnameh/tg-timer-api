from pydantic import BaseModel

class TimerItem(BaseModel):
    id: int
    title: str | None
    duration_ms: int
    order_index: int

class TimerSession(BaseModel):
    id: int
    chat_id: int
    creator_id: int
    status: str
    started_at_ms: int | None
