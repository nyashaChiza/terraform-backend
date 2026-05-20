from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.session import Session as WorkoutSession
from app.models.friendship import Friendship, SessionReaction
from app.models.enums import FriendshipStatus, SessionStatus, NotificationType
from app.schemas.feed import FeedSessionOut, ReactPayload
from app.core.notifications import create_notification

router = APIRouter(tags=["Feed"])


def _get_friend_ids(db: Session, user_id: int) -> List[int]:
    rows = (
        db.query(Friendship)
        .filter(
            (
                (Friendship.requester_id == user_id) |
                (Friendship.addressee_id == user_id)
            ),
            Friendship.status == FriendshipStatus.accepted,
        )
        .all()
    )
    return [
        r.addressee_id if r.requester_id == user_id else r.requester_id
        for r in rows
    ]


@router.get("/", response_model=List[FeedSessionOut])
def get_feed(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Return the 30 most recent completed sessions from friends, newest first.
    """
    friend_ids = _get_friend_ids(db, current_user.id)
    if not friend_ids:
        return []

    sessions = (
        db.query(WorkoutSession)
        .options(joinedload(WorkoutSession.user))   # avoid N+1 on user
        .filter(
            WorkoutSession.user_id.in_(friend_ids),
            WorkoutSession.status == SessionStatus.COMPLETED,
        )
        .order_by(WorkoutSession.completed_at.desc())
        .limit(30)
        .all()
    )

    result = []
    for s in sessions:
        # Fetch all reactions for this session (eager-load reactor to avoid N+1)
        reactions_rows = (
            db.query(SessionReaction)
            .options(joinedload(SessionReaction.reactor))
            .filter(SessionReaction.session_id == s.id)
            .all()
        )
        my_reaction = next(
            (r.emoji for r in reactions_rows if r.reactor_id == current_user.id), None
        )
        result.append(
            FeedSessionOut(
                session_id=s.id,
                user=s.user,
                title=s.title,
                summary=s.summary,
                intensity=s.intensity,
                estimated_duration_minutes=s.estimated_duration_minutes,
                completed_at=s.completed_at,
                reactions=[
                    {"id": r.id, "reactor": r.reactor, "emoji": r.emoji, "created_at": r.created_at}
                    for r in reactions_rows
                ],
                my_reaction=my_reaction,
            )
        )
    return result


@router.post("/{session_id}/react", status_code=status.HTTP_201_CREATED)
def react_to_session(
    session_id: int,
    payload: ReactPayload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    React to a friend's completed session with an emoji.
    If already reacted, updates the emoji.
    """
    # Verify session exists and belongs to a friend
    s = db.query(WorkoutSession).filter(
        WorkoutSession.id == session_id,
        WorkoutSession.status == SessionStatus.COMPLETED,
    ).first()
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")

    if s.user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot react to your own session")

    friend_ids = _get_friend_ids(db, current_user.id)
    if s.user_id not in friend_ids:
        raise HTTPException(status_code=403, detail="Not friends with this user")

    existing = (
        db.query(SessionReaction)
        .filter(
            SessionReaction.session_id == session_id,
            SessionReaction.reactor_id == current_user.id,
        )
        .first()
    )
    if existing:
        existing.emoji = payload.emoji
        db.commit()
    else:
        new_reaction = SessionReaction(
            session_id=session_id,
            reactor_id=current_user.id,
            emoji=payload.emoji,
        )
        db.add(new_reaction)
        db.commit()
        db.refresh(new_reaction)

        # Notify the session owner
        create_notification(
            db=db,
            user_id=s.user_id,
            type=NotificationType.reaction_received,
            actor_id=current_user.id,
            meta={"session_id": session_id, "emoji": payload.emoji},
        )

    return {"ok": True, "emoji": payload.emoji}


@router.delete("/{session_id}/react", status_code=status.HTTP_204_NO_CONTENT)
def remove_reaction(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove the current user's reaction from a session."""
    existing = (
        db.query(SessionReaction)
        .filter(
            SessionReaction.session_id == session_id,
            SessionReaction.reactor_id == current_user.id,
        )
        .first()
    )
    if not existing:
        raise HTTPException(status_code=404, detail="Reaction not found")
    db.delete(existing)
    db.commit()
