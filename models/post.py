from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from models.base_entity import BaseEntity
from database.database import Base

class Post(BaseEntity):
    __tablename__ = 'post'

    id = Column(Integer, primary_key=True, index=True)
    comment = Column(Text, nullable=True)
    path = Column(String(255), nullable=True)
    is_published = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey('app_user.id', ondelete='CASCADE'), nullable=True)
    category_id = Column(Integer, ForeignKey('category.id'), nullable=True)

    user = relationship("AppUser", back_populates="posts")
    category = relationship("Category", back_populates="posts")
    like_posts = relationship("LikePost", back_populates="post")
    comments = relationship("Comment", back_populates="post")
