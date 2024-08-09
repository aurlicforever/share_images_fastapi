from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship
from database.database import Base

class Country(Base):
    __tablename__ = 'country'

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(Integer, nullable=True)
    code = Column(String(10), nullable=True)
    name = Column(String(255), nullable=True)
    continent = Column(String(255), nullable=True)
    continent_code = Column(String(5), nullable=True)
    alpha3 = Column(String(5), nullable=True)
    is_active = Column(Boolean, default=True)

    users = relationship("AppUser", back_populates="country")
