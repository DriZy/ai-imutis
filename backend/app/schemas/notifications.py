"""Schemas for notifications endpoints."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class Notification(BaseModel):
    id: str
    title: str
    body: str
    created_at: datetime
    read: bool = False
    category: Optional[str] = Field(None, example="travel")


class NotificationList(BaseModel):
    notifications: List[Notification]


class SubscribeNotificationRequest(BaseModel):
    token: str = Field(..., description="FCM token")
    channels: List[str] = Field(default_factory=list)
