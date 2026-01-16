"""Notification endpoints and WebSocket stream."""
import asyncio
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import AuthenticatedUser, get_current_user, verify_token_string
from ..db import get_db
from ..models import Notification as NotificationModel, NotificationSubscription, User
from ..schemas.common import MessageResponse
from ..schemas.notifications import Notification, NotificationList, SubscribeNotificationRequest

router = APIRouter(prefix="/api", tags=["Notifications"])

async def _ensure_user(db: AsyncSession, user: AuthenticatedUser) -> None:
    existing = await db.get(User, user.uid)
    if existing:
        return
    db.add(User(uid=user.uid, email=user.email, role=user.role))
    await db.commit()


@router.get("/notifications", response_model=NotificationList)
async def list_notifications(
    user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> NotificationList:
    """Return notifications for the user."""

    await _ensure_user(db, user)
    result = await db.execute(select(NotificationModel).where(NotificationModel.user_id == user.uid))
    items = [
        Notification(
            id=n.id,
            title=n.title,
            body=n.body,
            created_at=n.created_at,
            read=n.read,
            category=n.category,
        )
        for n in result.scalars().all()
    ]
    return NotificationList(notifications=items)


@router.post("/notifications/subscribe", response_model=MessageResponse)
async def subscribe_notifications(
    payload: SubscribeNotificationRequest,
    user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Register an FCM token for push notifications (stored in memory)."""

    await _ensure_user(db, user)

    existing = await db.execute(
        select(NotificationSubscription).where(NotificationSubscription.token == payload.token)
    )
    record = existing.scalars().first()
    if record:
        record.channels = payload.channels or []
    else:
        db.add(
            NotificationSubscription(
                user_id=user.uid,
                token=payload.token,
                channels=payload.channels or [],
            )
        )
    await db.commit()
    return MessageResponse(message="Subscribed to notifications")


@router.delete("/notifications/{notification_id}", response_model=MessageResponse)
async def dismiss_notification(
    notification_id: str,
    user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Mark a notification as read (demo)."""

    await _ensure_user(db, user)
    notification = await db.get(NotificationModel, notification_id)
    if not notification or notification.user_id != user.uid:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")

    notification.read = True
    await db.commit()
    return MessageResponse(message="Notification dismissed")


@router.websocket("/ws/user/{user_id}/notifications")
async def notifications_ws(websocket: WebSocket, user_id: str) -> None:
    """Simple WebSocket stream that emits demo notifications."""

    token = websocket.query_params.get("token")
    auth_header = websocket.headers.get("Authorization", "")
    if not token and auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "", 1).strip()

    if not token:
        await websocket.close(code=4401)
        return

    try:
        user = await verify_token_string(token)
    except HTTPException:
        await websocket.close(code=4401)
        return

    if user.uid != user_id:
        await websocket.close(code=4403)
        return

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
