from sqlalchemy import Column, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship
from models.base_entity import BaseEntity
from database.database import Base

class Comment(BaseEntity):
    __tablename__ = 'comment'

    id = Column(Integer, primary_key=True, index=True)
    comment_text = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey('app_user.id', ondelete='CASCADE'), nullable=False)
    post_id = Column(Integer, ForeignKey('post.id', ondelete='CASCADE'), nullable=False)

    post = relationship("Post", back_populates="comments")
    user = relationship("AppUser", back_populates="comments")
