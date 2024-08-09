from sqlalchemy import Boolean, Column, ForeignKey, Integer
from sqlalchemy.orm import relationship
from database.database import Base
from models.base_entity import BaseEntity

class LikePost(BaseEntity):
    __tablename__ = 'like_post'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('app_user.id', ondelete='CASCADE'), nullable=False)
    post_id = Column(Integer, ForeignKey('post.id', ondelete='CASCADE'), nullable=False)
    is_liked = Column(Boolean, default=False)

    post = relationship("Post", back_populates="like_posts")
    user = relationship("AppUser", back_populates="like_posts")
