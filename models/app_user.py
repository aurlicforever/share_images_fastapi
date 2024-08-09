from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from database.database import Base
from datetime import datetime, timezone
from models.base_entity import BaseEntity

class AppUser(BaseEntity):
    __tablename__ = 'app_user'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=True)
    user_name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    password = Column(String(255), nullable=True)
    phone = Column(String(255), nullable=True)
    photo = Column(String(255), nullable=True)
    country_code = Column(String(50), nullable=True)
    phone_number = Column(String(50), nullable=True)
    is_confirmed = Column(Boolean, default=False)
    user_url = Column(String(255), nullable=True)
    folder = Column(String(255), nullable=True)
    code_confirmation = Column(String(255), nullable=True)
    code_confirmation_date = Column(DateTime(timezone=True), nullable=True, default=datetime.now(timezone.utc))
    country_id = Column(Integer, ForeignKey('country.id'), nullable=True)
    token = Column(String(255), nullable=True)
    refresh_token = Column(String(255), nullable=True)
    remember_token = Column(String(255), nullable=True)
    remember_token_expiry_time = Column(DateTime(timezone=True), nullable=True, default=datetime.now(timezone.utc))
    refresh_token_expiry_time = Column(DateTime(timezone=True), nullable=True, default=datetime.now(timezone.utc))

    country = relationship("Country", back_populates="users")
    posts = relationship("Post", back_populates="user")
    like_posts = relationship("LikePost", back_populates="user")
    comments = relationship("Comment", back_populates="user")

