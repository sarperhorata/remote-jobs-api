from sqlalchemy import Column, Integer, String, ARRAY
from ..database import Base

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, nullable=True)
    location = Column(String, nullable=True)
    job_type = Column(String, nullable=True)
    skills = Column(ARRAY(String), default=[])
    experience = Column(String, nullable=True)
    education = Column(String, nullable=True)
    languages = Column(ARRAY(String), default=[]) 