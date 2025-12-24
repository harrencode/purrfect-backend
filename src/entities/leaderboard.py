import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..database.core import Base
from sqlalchemy.ext.hybrid import hybrid_property

class LeaderboardUser(Base):
    __tablename__ = "leaderboard_users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    score = Column(Integer, nullable=False, default=0)
    last_active = Column(String, nullable=False)
    rescues = Column(Integer, nullable=False, default=0)
    adoptions = Column(Integer, nullable=False, default=0)
    lost_pets = Column(Integer, nullable=False, default=0)
    map_contributions = Column(Integer, nullable=False, default=0)
    avatar = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    

    # Relationship to user
    user = relationship("User", backref="leaderboard_entry", lazy="joined")

    @hybrid_property
    def avatar(self):
        # Dynamically return user's profile photo URL.
        return self.user.profile_photo_url if self.user else None

    def __repr__(self):
        return f"<LeaderboardUser(user_id='{self.user_id}', score={self.score})>"
