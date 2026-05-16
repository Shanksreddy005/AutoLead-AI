from sqlalchemy import Column, Integer, String, Text, DateTime
from database import Base
import datetime

class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, index=True)
    company_name = Column(String)
    company_url = Column(String)
    session_id = Column(String, unique=True, index=True)
    status = Column(String, default="Received")
    pdf_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
