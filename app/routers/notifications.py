"""Notification endpoints and WebSocket stream."""
import asyncio
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from .. import data
from ..dependencies import AuthenticatedUser, get_current_user
from ..schemas.common import MessageResponse
from ..schemas.notifications import Notification, NotificationList, SubscribeNotificationRequest

router = APIRouter(prefix="/api", tags=["Notifications"])

_subscriptions: List[str] = []


@router.get("/notifications", response_model=NotificationList)
async def list_notifications(
    user: AuthenticatedUser = Depends(get_current_user),
) -> NotificationList:
    """Return notifications for the user (demo data)."""

    items = [Notification(**n) for n in data.notifications]
    return NotificationList(notifications=items)


@router.post("/notifications/subscribe", response_model=MessageResponse)
async def subscribe_notifications(
    payload: SubscribeNotificationRequest,
    user: AuthenticatedUser = Depends(get_current_user),
) -> MessageResponse:
    """Register an FCM token for push notifications (stored in memory)."""

    if payload.token not in _subscriptions:
        _subscriptions.append(payload.token)
    return MessageResponse(message="Subscribed to notifications")


@router.delete("/notifications/{notification_id}", response_model=MessageResponse)
async def dismiss_notification(notification_id: str) -> MessageResponse:
    """Mark a notification as read (demo)."""

    for item in data.notifications:
        if item["id"] == notification_id:
            item["read"] = True
            return MessageResponse(message="Notification dismissed")
    return MessageResponse(message="Notification already dismissed")


@router.websocket("/ws/user/{user_id}/notifications")
async def notifications_ws(websocket: WebSocket, user_id: str) -> None:
    """Simple WebSocket stream that emits demo notifications."""

    await websocket.accept()
    try:
        await websocket.send_json({
            "message": "connected",
            "user_id": user_id,
            "at": datetime.utcnow().isoformat(),
        })
        while True:
            # Periodically send a keep-alive notification.
            await asyncio.sleep(15)
            await websocket.send_json({
                "type": "keepalive",
                "detail": "No new notifications",
                "at": datetime.utcnow().isoformat(),
            })
    except WebSocketDisconnect:
        return
