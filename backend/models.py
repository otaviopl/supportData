from enum import Enum
from typing import Optional
from pydantic import BaseModel


class TicketStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TicketChannel(str, Enum):
    EMAIL = "email"
    SLACK = "slack"
    WHATSAPP = "whatsapp"
    WEB = "web"
    PHONE = "phone"


class TicketBase(BaseModel):
    customer_name: str
    channel: TicketChannel
    subject: str
    description: Optional[str] = None
    status: TicketStatus
    priority: TicketPriority


class TicketCreate(TicketBase):
    created_at: Optional[str] = None


class TicketUpdate(BaseModel):
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None


class TicketResponse(TicketBase):
    id: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class TicketListResponse(BaseModel):
    items: list[TicketResponse]
    page: int
    page_size: int
    total: int


class TicketUpdateResponse(BaseModel):
    id: int
    status: TicketStatus
    priority: TicketPriority
    updated_at: str

