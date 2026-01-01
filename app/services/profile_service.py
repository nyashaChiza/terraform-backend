from sqlalchemy.orm import Session
from app.models.profile import Profile
from app.schemas.profile import ProfileCreate, ProfileUpdate

class ProfileService:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user(self, user_id: int) -> Profile | None:
        return self.db.query(Profile).filter(Profile.user_id == user_id).first()

    def create(self, user_id: int, profile_in: ProfileCreate) -> Profile:
        existing = self.get_by_user(user_id)
        if existing:
            raise ValueError("Profile already exists for this user")
        profile = Profile(user_id=user_id, **profile_in.model_dump())
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def update(self, profile: Profile, updates: ProfileUpdate) -> Profile:
        for field, value in updates.model_dump(exclude_unset=True).items():
            setattr(profile, field, value)
        self.db.commit()
        self.db.refresh(profile)
        return profile
