from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.friendship import Friendship
from app.models.enums import FriendshipStatus, NotificationType
from app.schemas.user import PublicUserOut
from app.schemas.friendship import FriendshipOut, FriendRequestIn, IncomingRequestOut
from app.core.notifications import create_notification

router = APIRouter(tags=["Friends"])


def _friendship_row(db, user_id: int, other_id: int):
    """Return the friendship row between two users (either direction), or None."""
    return (
        db.query(Friendship)
        .filter(
            (
                (Friendship.requester_id == user_id) & (Friendship.addressee_id == other_id)
            ) | (
                (Friendship.requester_id == other_id) & (Friendship.addressee_id == user_id)
            )
        )
        .first()
    )


@router.post("/request", status_code=status.HTTP_201_CREATED)
def send_friend_request(
    payload: FriendRequestIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Send a friend request to another user."""
    if payload.addressee_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot send a friend request to yourself")

    target = db.query(User).filter(User.id == payload.addressee_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    existing = _friendship_row(db, current_user.id, payload.addressee_id)
    if existing:
        if existing.status == FriendshipStatus.accepted:
            raise HTTPException(status_code=409, detail="Already friends")
        if existing.status == FriendshipStatus.pending:
            raise HTTPException(status_code=409, detail="Request already pending")
        # Declined → allow re-requesting; update direction in case it was reversed
        existing.status = FriendshipStatus.pending
        existing.requester_id = current_user.id
        existing.addressee_id = payload.addressee_id
        db.commit()
        db.refresh(existing)
    else:
        existing = Friendship(
            requester_id=current_user.id,
            addressee_id=payload.addressee_id,
            status=FriendshipStatus.pending,
        )
        db.add(existing)
        db.commit()
        db.refresh(existing)

    # Notify the addressee (always the intended recipient after direction is set)
    create_notification(
        db=db,
        user_id=existing.addressee_id,
        type=NotificationType.friend_request,
        actor_id=current_user.id,
    )

    return {"id": existing.id, "status": existing.status}


@router.post("/accept/{friendship_id}", status_code=status.HTTP_200_OK)
def accept_friend_request(
    friendship_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Accept an incoming friend request."""
    row = db.query(Friendship).filter(
        Friendship.id == friendship_id,
        Friendship.addressee_id == current_user.id,
        Friendship.status == FriendshipStatus.pending,
    ).first()
    if not row:
        raise HTTPException(status_code=404, detail="Pending request not found")

    row.status = FriendshipStatus.accepted
    db.commit()

    # Notify the original requester
    create_notification(
        db=db,
        user_id=row.requester_id,
        type=NotificationType.friend_accepted,
        actor_id=current_user.id,
    )

    return {"id": row.id, "status": row.status}


@router.post("/decline/{friendship_id}", status_code=status.HTTP_200_OK)
def decline_friend_request(
    friendship_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Decline an incoming friend request."""
    row = db.query(Friendship).filter(
        Friendship.id == friendship_id,
        Friendship.addressee_id == current_user.id,
        Friendship.status == FriendshipStatus.pending,
    ).first()
    if not row:
        raise HTTPException(status_code=404, detail="Pending request not found")

    row.status = FriendshipStatus.declined
    db.commit()
    return {"id": row.id, "status": row.status}


@router.delete("/remove/{other_user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_friend(
    other_user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove an existing friendship."""
    row = _friendship_row(db, current_user.id, other_user_id)
    if not row or row.status != FriendshipStatus.accepted:
        raise HTTPException(status_code=404, detail="Friendship not found")
    db.delete(row)
    db.commit()


@router.get("/", response_model=List[PublicUserOut])
def get_friends(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return all accepted friends for the current user."""
    rows = (
        db.query(Friendship)
        .options(
            joinedload(Friendship.requester),
            joinedload(Friendship.addressee),
        )
        .filter(
            (
                (Friendship.requester_id == current_user.id) |
                (Friendship.addressee_id == current_user.id)
            ),
            Friendship.status == FriendshipStatus.accepted,
        )
        .all()
    )
    friends = []
    for row in rows:
        other = row.addressee if row.requester_id == current_user.id else row.requester
        friends.append(other)
    return friends


@router.get("/requests/incoming", response_model=List[IncomingRequestOut], response_model_by_alias=True)
def get_incoming_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return all pending friend requests sent TO the current user."""
    rows = (
        db.query(Friendship)
        .options(joinedload(Friendship.requester))   # avoid N+1 on requester
        .filter(
            Friendship.addressee_id == current_user.id,
            Friendship.status == FriendshipStatus.pending,
        )
        .all()
    )
    return [
        IncomingRequestOut(
            friendship_id=r.id,
            from_user=r.requester,
            created_at=r.created_at,
        )
        for r in rows
    ]


@router.get("/status/{other_user_id}")
def get_friendship_status(
    other_user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Return the friendship status between the current user and another user.
    Possible values: none | pending_sent | pending_received | friends
    """
    row = _friendship_row(db, current_user.id, other_user_id)
    if not row:
        return {"status": "none"}
    if row.status == FriendshipStatus.accepted:
        return {"status": "friends"}
    if row.status == FriendshipStatus.pending:
        if row.requester_id == current_user.id:
            return {"status": "pending_sent"}
        return {"status": "pending_received", "friendship_id": row.id}
    return {"status": "none"}
