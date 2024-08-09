from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from models.base_entity import BaseEntity
from database.database import Base

class Category(BaseEntity):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)

    posts = relationship("Post", back_populates="category")